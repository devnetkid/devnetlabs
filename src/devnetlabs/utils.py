import logging
import os
import platform

logger = logging.getLogger(__name__)

def colorme(msg, color):
    """
    Sets the terminal color requested, defaults to white

    Args:
        color (str): Sets the color of text displayed on the terminal
    """
    if color == "red":
        logger.debug("Setting terminal color to red")
        wrapper = "\033[91m"
    elif color == "blue":
        logger.debug("Setting terminal color to blue")
        wrapper = "\033[94m"
    elif color == "green":
        logger.debug("Setting terminal color to green")
        wrapper = "\033[92m"
    else:
        # Defaults to white if invalid color is given
        logger.debug("Invalid color {color}, setting terminal color to white")
        wrapper = "\033[47m"
    return wrapper + msg + "\033[0m"


def clear_screen():
    """
    Runs the terminal clear screen command for the OS used
    """
    if platform.system().lower() == "windows":
        logger.debug("Sending the cls command to the terminal")
        cmd = "cls"
    else:
        logger.debug("Sending the clear command to the terminal")
        cmd = "clear"
    os.system(cmd)


# https://patohttps://patooftware/taag/ using font "ghosts"

menu_title1 = colorme(
r"""
 ____             _   _      _   _          _         
|  _ \  _____   _| \ | | ___| |_| |    __ _| |__  ___ 
| | | |/ _ \ \ / /  \| |/ _ \ __| |   / _` | '_ \/ __|
| |_| |  __/\ V /| |\  |  __/ |_| |__| (_| | |_) \__ \
|____/ \___| \_/ |_| \_|\___|\__|_____\__,_|_.__/|___/
""",
    "red",
)

menu_title2 = colorme(
r"""
 _____                                                        _____ 
( ___ )------------------------------------------------------( ___ )
 |   |                                                        |   | 
 |   |  ____             _   _      _   _          _          |   | 
 |   | |  _ \  _____   _| \ | | ___| |_| |    __ _| |__  ___  |   | 
 |   | | | | |/ _ \ \ / /  \| |/ _ \ __| |   / _` | '_ \/ __| |   | 
 |   | | |_| |  __/\ V /| |\  |  __/ |_| |__| (_| | |_) \__ \ |   | 
 |   | |____/ \___| \_/ |_| \_|\___|\__|_____\__,_|_.__/|___/ |   | 
 |___|                                                        |___| 
(_____)------------------------------------------------------(_____)
""",
    "red",
)

