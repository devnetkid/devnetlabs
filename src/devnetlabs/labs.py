import logging

from devnetlabs import menu, utils

logger = logging.getLogger(__name__)


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
    lab_name = input("Enter the name of the existing eve-ng lab: ")
    logger.debug(f"Building toml file from eve-ng lab {lab_name}")
    input("Press [ENTER] to continue...")


def devnetlabs_exit():
    """
    Clears the screen, logs an exit message, and terminates the application.
    """
    utils.clear_screen()
    logger.debug("Exiting application")
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
