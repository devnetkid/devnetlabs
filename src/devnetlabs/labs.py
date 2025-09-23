import logging

from devnetlabs import eveng, menu, utils

logger = logging.getLogger(__name__)

# Create an eveng client to interact with the eveng api
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


def build_toml_from_lab():
    """
    Returns a toml formatted file representing the specified eve-ng lab
    """
    toml_data = {}
    lab_exists = False
    lab_name = input("Enter the name of the existing eve-ng lab: ")
    logger.debug(f"Building toml file from eve-ng lab {lab_name}")
    file_lab_name = input("Enter the name of the file to be written: ")
    client.login()
    response = client.list_labs()
    if response["code"] == 200:
        for lab in response["data"]["labs"]:
            if lab_name in lab["file"]:
                lab_exists = True
    if lab_exists:
        # Prepare the lab details
        lab_data = client.get_lab(lab_name)["data"]
        lab_data.pop("id")
        lab_data.pop("filename")
        lab_data["path"] = "/"
        lab_data["name"] = "devnetlab"
        toml_data["lab"] = lab_data
        # Prepare the nodes
        nodes = list()
        lab_nodes = client.get_lab_nodes(lab_name)["data"]
        for node in lab_nodes.values():
            node.pop("url")
            node.pop("ram")
            node.pop("cpu")
            node.pop("uuid")
            node.pop("config")
            node.pop("config_list")
            nodes.append(node)
        toml_data["nodes"] = nodes
        # Prepare the cables
        lab_cables = client.get_lab_topology(lab_name)["data"]
        for cable in lab_cables:
            cable.pop("network_id")
        toml_data["cables"] = lab_cables
        if utils.write_toml(file_lab_name, toml_data):
            logger.info(f"Successfully saved lab '{lab_name}' to file '{file_lab_name}'")
        else:
            logger.debug(f"User chose not to overwrite file '{file_lab_name}'")
    else:
        print("The lab you requested does not exist")
    input("Press [ENTER] to continue...")


def create_lab():
    """
    Creates a new lab in eve-ng based on the contents of a toml config file.
    """
    config = input("Enter the name of the config file to load: ")
    logger.info(f"Loading config file '{config}'")
    new_lab = utils.load_toml(config)
    logger.debug(f"Contents of '{config}'\n{new_lab}")
    client.login()
    logger.debug(f"Calling create_lab with args {new_lab["lab"]}")
    response = client.create_lab(new_lab["lab"])
    logger.debug(f"Response from calling create_lab\n{response}")
    if response["code"] == 200:
        for node in new_lab["nodes"]:
            logger.debug(f"Calling create_node with args {new_lab["lab"]["name"]}, {node}")
            client.create_node(new_lab["lab"]["name"], node)
            logger.debug(f"Response from calling create_node\n{response}")
        for cable in new_lab["cables"]:
            logger.debug(f"The cable is: \n{cable}")
            src_node = cable.get("source")
            dst_node = cable.get("destination")
            nodes = client.get_lab_nodes(new_lab["lab"]["name"])
            nodes = nodes["data"]
            logger.debug(f"The nodes list is: \n{nodes}")
            # Find the node ID based on node name
            for key, value in nodes.items():
                if value["name"] == src_node:
                    src_node_id = value["id"]
                if value["name"] == dst_node:
                    dst_node_id = value["id"]
            # Find link IDs
            src_label = cable.get("source_label")
            dst_label = cable.get("destination_label")
            # Get the interface index to be used for connection
            src_node_ports = client.get_intf(new_lab["lab"]["name"], src_node_id)["data"]["ethernet"]
            logger.debug(f"The source node ports is: \n{src_node_ports}")
            for index, item in enumerate(src_node_ports):
                if src_label == item["name"]:
                    src_intf_id = index
            # Get the interface index to be used for connection
            dst_node_ports = client.get_intf(new_lab["lab"]["name"], dst_node_id)["data"]["ethernet"]
            logger.debug(f"The destination node ports is: \n{dst_node_ports}")
            for index, item in enumerate(dst_node_ports):
                if dst_label == item["name"]:
                    dst_intf_id = index
            # Create the network bridge for the connection
            bid_data = {"name":"Net-1","type":"bridge","left":940,"top":196,"visibility":1}
            logger.debug(f"Calling create_network with args {new_lab["lab"]["name"]} and {bid_data}")
            bid_result = client.create_network(new_lab["lab"]["name"], bid_data)
            logger.debug(f"Response from calling create_network\n{bid_result}")
            bid = bid_result["data"].get("id")
            # Create network connection between two nodes
            connection_data = {str(src_intf_id): bid}
            client.set_intf(new_lab["lab"]["name"], src_node_id, connection_data)
            logger.debug(f"The set interface is: \n{bid_result}")
            connection_data = {dst_intf_id: str(bid)}
            client.set_intf(new_lab["lab"]["name"], dst_node_id, connection_data)
            logger.debug(f"The set interface is: \n{bid_result}")
            # Hide network bridge in the GUI
            client.modify_network(new_lab["lab"]["name"], bid, {"visibility":0})
        print("Lab has been successfully created")
        logger.info(f"Successfully created lab {config}")
    elif response["code"] == 400:
        logger.debug(f"Failed to load and create lab {config}")
        print(utils.colorme(response["message"], "red"))
    else:
        print(utils.colorme(response["message"], "red"))
    input("Press [ENTER] to continue...")


def delete_lab():
    """
    Delete a lab from eve-ng
    """
    lab_name = input("Enter the name of the lab to delete: ")
    client.login()
    response = client.delete_lab(lab_name)
    print(response)
    input("Press [ENTER] to continue...")


def devnetlabs_exit():
    """
    Clears the screen, logs an exit message, and terminates the application.
    """
    utils.clear_screen()
    client.logout()
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
