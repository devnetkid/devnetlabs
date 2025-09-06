import logging
from collections import namedtuple

from devnetlabs import utils

logger = logging.getLogger(__name__)

class Menu:
    """
    A class that handles the display and interaction logic of a terminal-based menu.

    Attributes:
        _title (str): The title displayed at the top of the menu.
        _subtitle (str): A subtitle providing additional context.
        _options (list): A list of menu options, each a namedtuple with 'label' and 'callback'.
    """
    def __init__(self, title, subtitle, options):
        """
        Initializes the Menu instance.

        Args:
            title (str): The main title of the menu.
            subtitle (str): The subtitle displayed below the title.
            options (list[tuple[str, callable]]): A list of (label, callback) tuples.
                - label (str): The text shown for the menu item.
                - callback (callable): The function to call when the option is selected.
        """
        MenuItem = namedtuple("Option", ["label", "callback"])
        self._title = title
        self._subtitle = subtitle
        self._options = [MenuItem(*option) for option in options]

    def display(self):
        """
        Clears the screen and displays the menu with all available options.
        """
        utils.clear_screen()
        print(self._title)
        print(f"  {self._subtitle}\n")

        # Build and display each menu item with a number and colored label
        menu_items = ""
        for i, option in enumerate(self._options, start=1):
            menu_items += utils.colorme(f"    {i} - {option.label}\n", "green")
        print(menu_items)

    def get_input(self):
        """
        Prompts the user to select a menu option by number.

        Returns:
            The result of the callback function associated with the selected option.
        """
        while True:
            try:
                self.display()
                selection = int(input("\n  Select an option >> "))

                # Validate selection range
                if selection not in range(1, len(self._options) + 1):
                    print("\n  Entry not in range, please try again.")
                    input("  Press Enter to continue...\n")
                    continue

                self.display()  # Re-display menu before executing callback
                return self._options[selection - 1].callback()

            except ValueError:
                print("\n  Entry must be a number, please try again.")
                input("  Press Enter to continue...\n")
                continue

def jlabs_exit():
    """
    Clears the screen, logs an exit message, and terminates the application.
    """
    utils.clear_screen()
    logger.info("Exiting application")
    raise SystemExit("")


def menu():
    """
    Displays the main menu and handles user input in an infinite loop.
    """
    menu_title = utils.menu_title2
    menu_subtitle = "Main Menu"
    logger.debug("Creating instance of class Menu")
    menu = Menu(
        menu_title,
        menu_subtitle,
        [
            ("Exit", jlabs_exit),
        ],
    )
    while True:
        menu.get_input()
