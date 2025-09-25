# src/devnetlabs/labs.py

import logging

from devnetlabs import eveng, menu, utils

logger = logging.getLogger(__name__)

# Create an eveng client
client = eveng.EveNgClient("192.168.11.99")


def labs():
    """
    Displays a sub-menu for lab options
    """
    menu_title = utils.menu_title1
    menu_subtitle = "Labs Menu"
    labs_menu = menu.Menu(
        menu_title,
        menu_subtitle,
        [
            ("Build toml from existing lab", build_toml_from_lab),
            ("Create a lab from toml", create_lab),
            ("Delete a lab", delete_lab),
            ("Return to the main menu", main_menu),
            ("Exit", devnetlabs_exit),
        ],
    )
    while True:
        labs_menu.get_input()


def define_lab_details(lab_data):
    """
    Define the parameters needed to create a new lab
    """
    # Remove items that are not needed for a new lab
    lab_data.pop("id")
    lab_data.pop("lock")
    lab_data.pop("filename")
    # Add items not in existing lab
    lab_data["path"] = "/"
    # Rename the lab so it doesn't conflict with existing
    current_name = lab_data["name"]
    lab_data["name"] = f"{current_name}temp"
    return lab_data


def build_nodes_list(lab_nodes):
    """
    Builds a list of nodes removing items that aren't needed to re-create the lab

    Args:
        lab_nodes (dict): A dictionary obtained from an existing eve-ng lab.

    Returns:
        nodes (list): A list of dictionaries describing how to configure a node.
        node_map (list): A list of dictionaries mapping an ID to a name.
    """
    nodes = []
    node_map = []
    for node in lab_nodes.values():
        # Remove items that are not needed for a new lab
        node.pop("url")
        node.pop("uuid")
        node.pop("config")
        node.pop("config_list")
        nodes.append(node)
        node_map.append({f"node{node['id']}": node["name"]})
    return nodes, node_map


def build_cable_list(lab_cables, node_map):
    """
    Builds a list of cable connections from an existing eve-ng lab.
    Replaces node IDs with names and removes unnecessary fields.
    """
    # Flatten node_map into a single lookup dictionary
    node_lookup = {}
    for node in node_map:
        node_lookup.update(node)

    cables = []
    for cable in lab_cables:
        cable = {k: v for k, v in cable.items() if k != "network_id"}
        cable["source"] = node_lookup.get(cable["source"], cable["source"])
        cable["destination"] = node_lookup.get(cable["destination"], cable["destination"])
        cables.append(cable)

    return cables


def build_toml_from_lab():
    """
    Returns a toml formatted file representing the specified eve-ng lab
    """
    toml_data = {}
    # Prompt user for the name of an existing eve-ng lab
    lab_name = input("Enter the name of the existing eve-ng lab: ")
    logger.debug(f"Building toml file from eve-ng lab {lab_name}")

    # Get existing lab information
    try:
        client.login()
        lab_data = client.get(f"labs/{lab_name}.unl")["data"]
        logger.debug(f"Response from get lab\n{lab_data}")
        lab_nodes = client.get(f"labs/{lab_name}.unl/nodes")["data"]
        logger.debug(f"Response from getting nodes\n{lab_nodes}")
        lab_cables = client.get(f"labs/{lab_name}.unl/topology")["data"]
        logger.debug(f"Response from getting topology\n{lab_cables}")
        client.logout()
    except requests.exceptions.RequestException as err:
        print(f"An error occurred: \n{err}")

    # Prepare the lab details
    toml_data["lab"] = define_lab_details(lab_data)

    # Prepare the nodes
    nodes, node_map = build_nodes_list(lab_nodes)
    toml_data["nodes"] = nodes

    # Prepare the cables
    toml_data["cables"] = build_cable_list(lab_cables, node_map)

    # Write data to a toml file
    if utils.write_toml(lab_name + ".toml", toml_data):
        logger.info(f"Successfully saved lab '{lab_name}' to file '{lab_name}.toml'")
    else:
        logger.debug(f"User chose not to overwrite file '{file_lab_name}'")
    input("Press [ENTER] to continue...")


def find_node_id_by_name(nodes, src_node, dst_node):
    src_node_id = dst_node_id = ""
    for key, value in nodes.items():
        if value["name"] == src_node:
            src_node_id = value["id"]
        if value["name"] == dst_node:
            dst_node_id = value["id"]
    return src_node_id, dst_node_id


def get_interface_index(ports, label):
    for index, item in enumerate(ports):
        if label == item["name"]:
            intf_id = index
    return str(intf_id)


def create_lab():
    """
    Creates a new lab in eve-ng based on the contents of a toml config file.
    """
    config_file = input("Enter the name of the config file to load: ")
    logger.info(f"Loading config file '{config_file}'")
    config = utils.load_toml(config_file)
    logger.debug(f"Contents of '{config_file}'\n{config}")
    lab_name = config["lab"]["name"] + ".unl"

    # Create lab from config file
    try:
        client.login()
        client.post("labs", config["lab"])
        for node in config["nodes"]:
            client.post(f"labs/{lab_name}/nodes", node)
        nodes = client.get(f"labs/{lab_name}/nodes")["data"]
        for cable in config["cables"]:
            src_node = cable.get("source")
            dst_node = cable.get("destination")
            src_label = cable.get("source_label")
            dst_label = cable.get("destination_label")
            # Find node ID by finding the node name that matches the node specified by cable
            src_node_id, dst_node_id = find_node_id_by_name(nodes, src_node, dst_node)
            src_node_ports = client.get(f"labs/{lab_name}/nodes/{src_node_id}/interfaces")["data"]["ethernet"]
            dst_node_ports = client.get(f"labs/{lab_name}/nodes/{dst_node_id}/interfaces")["data"]["ethernet"]
            # Create the network bridge for the connection
            bid_data = {"name":"Net-1","type":"bridge","left":940,"top":196,"visibility":1}
            bid_result = client.post(f"labs/{lab_name}/networks", bid_data)
            bid = bid_result["data"].get("id")
            # Create network connection between two nodes
            src_idx = get_interface_index(src_node_ports, src_label)
            dst_idx = get_interface_index(dst_node_ports, dst_label)
            client.put(f"labs/{lab_name}/nodes/{src_node_id}/interfaces", {src_idx: bid})
            client.put(f"labs/{lab_name}/nodes/{dst_node_id}/interfaces", {dst_idx: bid})
            # Hide network bridge in the GUI
            client.put(f"labs/{lab_name}/networks/{bid}", {"visibility":0})
    except Exception as err:
        print(f"An error occurred: \n{err}")
    finally:
        client.logout()
        
    input("Press [ENTER] to continue...")


def delete_lab():
    """
    Delete a lab from eve-ng
    """
    lab_name = input("Enter the name of the lab to delete: ")
    url = f"labs/{lab_name}.unl"
    try:
        client.login()
        response = client.delete(url)
        logger.debug(f"Deleted lab {lab_name}, response from server was {response}")
    except Exception as err:
        print(f"An error occurred: \n{err}")
    finally:
        client.logout()
    print(f"The eve-ng lab '{lab_name}' has been deleted.")
    input("Press [ENTER] to continue...")


def devnetlabs_exit():
    """
    Clears the screen, logs an exit message, and terminates the application.
    """
    utils.clear_screen()
    logger.info("Exiting application")
    raise SystemExit("")


def main_menu():
    """
    Displays the main menu and handles user input in an infinite loop.
    """
    menu_title = utils.menu_title1
    menu_subtitle = "Main Menu"
    main_menu = menu.Menu(
        menu_title,
        menu_subtitle,
        [
            ("Lab Options", labs),
            ("Exit", devnetlabs_exit),
        ],
    )
    while True:
        main_menu.get_input()
