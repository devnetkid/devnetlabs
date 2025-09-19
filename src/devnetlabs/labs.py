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
    res = client.list_labs()
    if res["code"] == 200:
        for lab in res["data"]["labs"]:
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
    Creates a new lab
    """
    config = input("Enter the name of the config file to load: ")
    logger.info(f"Loading config file '{config}'")
    new_lab = utils.load_toml(config)
    logger.debug(f"Contents of '{config}'\n{new_lab}")
    client.login()
    if client.create_lab(new_lab["lab"]):
        logger.info(f"Successfully created lab {config}")
    else:
        logger.debug(f"Failed to load and create lab {config}")


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
