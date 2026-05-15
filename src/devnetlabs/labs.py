# src/devnetlabs/labs.py

# src/devnetlabs/labs.py

import logging
import os
import requests
import time
import sys
from pathlib import Path

from devnetlabs import connector, eveng, menu, utils

logger = logging.getLogger(__name__)

# BEST PRACTICE: Use environment variables for sensitive/environment-specific data
EVENG_IP = os.getenv("EVENG_IP", "192.168.11.99")
client = eveng.EveNgClient(EVENG_IP)


def define_lab_details(lab_data: dict) -> dict:
    """Define the parameters needed to create a new lab."""
    for key in ["id", "lock", "filename"]:
        lab_data.pop(key, None)
    
    lab_data["path"] = "/"
    lab_data["name"] = f"{lab_data.get('name', 'unnamed')}_temp"
    return lab_data


def build_nodes_list(lab_nodes: dict) -> tuple[list, list]:
    """Builds a list of nodes removing items that aren't needed to re-create the lab."""
    nodes = []
    node_map = []
    for node in lab_nodes.values():
        for key in ["url", "uuid", "config", "config_list"]:
            node.pop(key, None)
        nodes.append(node)
        node_map.append({f"node{node['id']}": node["name"]})
    return nodes, node_map


def build_cable_list(lab_cables: list, node_map: list) -> list:
    """Builds a list of cable connections from an existing eve-ng lab."""
    node_lookup = {}
    for node in node_map:
        node_lookup.update(node)

    cables = []
    for cable in lab_cables:
        new_cable = {k: v for k, v in cable.items() if k != "network_id"}
        new_cable["source"] = node_lookup.get(new_cable["source"], new_cable["source"])
        new_cable["destination"] = node_lookup.get(new_cable["destination"], new_cable["destination"])
        cables.append(new_cable)

    return cables


def build_toml_from_lab():
    """Returns a toml formatted file representing the specified eve-ng lab."""
    toml_data = {}
    lab_name = input("Enter the name of the existing eve-ng lab: ").strip()
    logger.debug(f"Building toml file from eve-ng lab {lab_name}")

    try:
        client.login()
        lab_data = client.get(f"labs/{lab_name}.unl").get("data")
        lab_nodes = client.get(f"labs/{lab_name}.unl/nodes").get("data", {})
        lab_cables = client.get(f"labs/{lab_name}.unl/topology").get("data", [])
    except requests.exceptions.RequestException as err:
        print(f"A network error occurred communicating with EVE-NG: \n{err}")
        return
    finally:
        client.logout()

    if not lab_data:
        print("No lab data found.")
        return

    toml_data["lab"] = define_lab_details(lab_data)
    nodes, node_map = build_nodes_list(lab_nodes)
    toml_data["nodes"] = nodes
    toml_data["cables"] = build_cable_list(lab_cables, node_map)

    file_name = f"{lab_name}.toml"
    if utils.write_toml(file_name, toml_data):
        logger.info(f"Successfully saved lab '{lab_name}' to file '{file_name}'")
        print(f"Successfully saved to {file_name}")
    else:
        logger.debug(f"User chose not to overwrite file '{file_name}'")
        
    input("Press [ENTER] to continue...")


def find_node_id_by_name(nodes: dict, src_node: str, dst_node: str) -> tuple[str, str]:
    src_node_id = dst_node_id = ""
    for value in nodes.values():
        if value["name"] == src_node:
            src_node_id = value["id"]
        if value["name"] == dst_node:
            dst_node_id = value["id"]
    return src_node_id, dst_node_id


def get_interface_index(ports: list, label: str) -> str:
    for index, item in enumerate(ports):
        if label == item["name"]:
            return str(index)
    return ""


def create_lab(config_data: dict = None):
    """Creates a new lab in eve-ng based on the contents of a toml config file."""
    if not config_data:
        config_file = input("Enter the name of the config file to load: ").strip()
        logger.info(f"Loading config file '{config_file}'")
        try:
            config_data = utils.load_toml(config_file)
        except Exception as e:
            print(f"Error loading {config_file}: {e}")
            return
            
    lab_name = f"{config_data['lab']['name']}.unl"

    logger.info(f"Checking if lab {lab_name} already exists.")
    try:
        client.login()
        response = client.get(f"labs/{lab_name}")
        if response.get("code") == 200:
            logger.warning(f"The lab {lab_name} already exists.")
            print(f"The lab {lab_name} already exists.")
            return # Don't exit(), just return to previous menu
    except requests.exceptions.RequestException:
        logger.info("Confirmed lab does not exist, attempting to create lab.")

    try:
        client.post("labs", config_data["lab"])
        for node in config_data.get("nodes", []):
            client.post(f"labs/{lab_name}/nodes", node)
            
        nodes = client.get(f"labs/{lab_name}/nodes")["data"]
        
        for cable in config_data.get("cables", []):
            src_node, dst_node = cable.get("source"), cable.get("destination")
            src_label, dst_label = cable.get("source_label"), cable.get("destination_label")
            
            src_node_id, dst_node_id = find_node_id_by_name(nodes, src_node, dst_node)
            
            src_node_ports = client.get(f"labs/{lab_name}/nodes/{src_node_id}/interfaces")["data"]["ethernet"]
            dst_node_ports = client.get(f"labs/{lab_name}/nodes/{dst_node_id}/interfaces")["data"]["ethernet"]
            
            bid_data = {"name": "Net-1", "type": "bridge", "left": 940, "top": 196, "visibility": 1}
            bid_result = client.post(f"labs/{lab_name}/networks", bid_data)
            bid = bid_result["data"].get("id")
            
            src_idx = get_interface_index(src_node_ports, src_label)
            dst_idx = get_interface_index(dst_node_ports, dst_label)
            
            client.put(f"labs/{lab_name}/nodes/{src_node_id}/interfaces", {src_idx: bid})
            client.put(f"labs/{lab_name}/nodes/{dst_node_id}/interfaces", {dst_idx: bid})
            client.put(f"labs/{lab_name}/networks/{bid}", {"visibility": 0})
            
        logger.info("The lab was successfully created.")
        print(f"Successfully created lab {lab_name}")
        
    except Exception as err:
        print(f"An error occurred creating the lab: \n{err}")
    finally:
        client.logout()


def delete_lab():
    """Delete a lab from eve-ng"""
    lab_name = input("Enter the name of the lab to delete: ").strip()
    url = f"labs/{lab_name}.unl"
    try:
        client.login()
        response = client.delete(url)
        logger.debug(f"Deleted lab {lab_name}, response from server was {response}")
        print(f"The eve-ng lab '{lab_name}' has been deleted.")
    except requests.exceptions.RequestException as err:
        print(f"Failed to delete lab: \n{err}")
    finally:
        client.logout()
    input("Press [ENTER] to continue...")


def start_nodes(lab: str, nodes: list):
    """Starts each node listed in the lab_settings."""
    logger.info("Starting lab nodes")
    for node in nodes:
        node_name = node.get('name', 'Unknown')
        logger.info(f"Starting node {node_name} ...")
        print(f"Starting node {node_name} ...")
        
        endpoint = f"labs/{lab}.unl/nodes/{node['id']}/start"
        try:
            client.login()
            client.get(endpoint)
        except requests.exceptions.RequestException as e:
            logger.error(f"Error starting node {node_name}: {e}")
        time.sleep(5)


def get_node_status(lab: str, node: dict) -> dict:
    """Fetches node details and extracts status and telnet port."""
    if not lab.endswith(".unl"):
        lab = f"{lab}.unl"

    endpoint = f"labs/{lab}/nodes/{node['id']}"
    client.login()
    response = client.get(endpoint)
    
    node_data = response.get('data', {})
    status = node_data.get('status')
    url = node_data.get('url', "")
    
    telnet_ip = telnet_port = eve_ip = None
    
    if ":" in url:
        telnet_ip = url.split(":")[-2]
        telnet_port = url.split(":")[-1]

    if telnet_ip and "//" in telnet_ip:
        eve_ip = telnet_ip.lstrip("//")
    
    return {
        "name": node_data.get('name'),
        "type": node_data.get("type"),
        "status": status,
        "port": telnet_port,
        "eve_ip": eve_ip,
    }


def load_base_configs(lab: str, lab_name: str, nodes: list):
    logger.info("Loading base configs...")
    
    for node in nodes:
        delay = 10
        max_attempts = 30
        node_name = node['name']
        logger.info(f"Current node {node_name}")

        # Build the dynamic path for the config file
        config_path = f"{lab}/configs/{node_name}.cfg"
        config_lines = utils.load_config(config_path)
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Attempt {attempt}: loading config for node {node_name}")
            node_info = get_node_status(lab_name, node)
            print(f"Waiting for node {node_info['name']} to complete booting ...")
            
            if node_info["type"] == "qemu" and node_info["eve_ip"] and node_info["port"]:
                device_settings = {
                    "device_ip": node_info["eve_ip"],
                    "device_type": "cisco_ios_telnet",
                    "port": node_info["port"],
                    "username": "admin",
                    "password": "cisco"
                }
                
                device = connector.DeviceConnection(**device_settings)
                
                try:
                    device.connect()
                    device.write_config(config_lines)
                    device.disconnect()
                    print(f"Successfully loaded config for {node_name}")
                    break # Success, exit retry loop
                except Exception as e:
                    logger.debug(f"SSH/Telnet not ready yet: {e}")
            
            time.sleep(delay)


def devnetlabs_exit():
    """Clears the screen, logs an exit message, and terminates the application."""
    utils.clear_screen()
    logger.info("Exiting application")
    sys.exit(0)


def load_lab(lab: str):
    logger.info(f"Loading lab.toml file from {lab}")
    filename = Path(lab) / "lab.toml"
    
    try:
        lab_settings = utils.load_toml(str(filename))
        create_lab(lab_settings)
        lab_name = lab_settings["lab"]["name"]
        lab_nodes = lab_settings.get("nodes", [])
        
        start_nodes(lab_name, lab_nodes)
        load_base_configs(lab, lab_name, lab_nodes)
    except Exception as e:
        print(f"Failed to load lab {lab}: {e}")


def list_lab():
    """List the available lab exercises"""
    labs = utils.list_dir()
    if not labs:
        print("No labs found.")
        input("Press [ENTER] to continue...")
        return

    for index, lab in enumerate(labs, start=1):
        print(f"{index} - {lab}")
        
    response = input("\nEnter the number next to the lab you would like to run: ")
    
    # BEST PRACTICE: Input Validation
    try:
        choice_idx = int(response) - 1
        if choice_idx < 0 or choice_idx >= len(labs):
            raise IndexError
        load_lab(labs[choice_idx])
    except (ValueError, IndexError):
        print("Invalid selection. Please enter a valid number from the list.")
    
    input("Press [ENTER] to continue...")


def labs_menu_view():
    """Displays the available lab exercises"""
    menu_title = utils.menu_title1
    menu_subtitle = "Labs Menu"
    labs_menu = menu.Menu(
        menu_title,
        menu_subtitle,
        [
            ("Load a lab", list_lab),
            ("Return to the main menu", main_menu),
            ("Exit", devnetlabs_exit),
        ],
    )
    while True:
        labs_menu.get_input()


def eveng_tools():
    """Displays a sub-menu for lab options"""
    menu_title = utils.menu_title1
    menu_subtitle = "Eve-NG Tools"
    tools_menu = menu.Menu(
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
        tools_menu.get_input()


def main_menu():
    """Displays the main menu and handles user input in an infinite loop."""
    menu_title = utils.menu_title1
    menu_subtitle = "Main Menu"
    main_menu = menu.Menu(
        menu_title,
        menu_subtitle,
        [
            ("Labs", labs_menu_view),
            ("Eve-NG Tools", eveng_tools),
            ("Exit", devnetlabs_exit),
        ],
    )
    while True:
        main_menu.get_input()






















































































































































































































































































































































































































