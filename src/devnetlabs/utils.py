import logging
import os
import platform
from datetime import datetime
from pathlib import Path

import toml


def setup_environment():
    # Define base directories
    base_dir = Path.home() / "devnetlabs"
    logs_dir = base_dir / "logs"
    labs_dir = base_dir / "labs"

    # Create folders if they don't exist
    logs_dir.mkdir(parents=True, exist_ok=True)
    labs_dir.mkdir(parents=True, exist_ok=True)

    # Dynamically create the log filename using current timestamp
    #logname = f"devnetlabs_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"
    log_file = "devnetlabs.log"

    # Check environment variables for log level, defaults to info if none provided
    log_level = getattr(logging, os.getenv("LABS_LOG_LEVEL", "info").upper(), None)
    if not isinstance(log_level, int):
        raise ValueError("Invalid log level")

    # Configure logging
    logging.basicConfig(
        filename=logs_dir / log_file,
        filemode="w",
        encoding="utf-8",
        level=log_level,
        format="%(asctime)s %(filename)20s:%(lineno)s %(levelname)11s > %(message)s",
        datefmt="%m/%d/%Y %I:%M:%S %p",
    )


def write_toml(filename, content):
    """
    Saves toml data to a file, prompting to overwrite if the file already exists.

    Args:
        filename (str): The file name.
        content (str): The toml data to write to the file.
    """
    config_path = Path.home() / "devnetlabs/labs/" / filename
    if config_path.exists():
        overwrite = input(f"File {filename} already exists. Overwrite? (y/n): ").lower()
        if overwrite != "y":
            print("File not saved.")
            return False
    try:
        with open(config_path, "w") as f:
            toml.dump(content, f)
        print(f"File '{config_path}' saved successfully.")
        return True
    except IOError as err:
        print(f"Error saving file '{config_path}': {err}")


def load_toml(filename):
    """
    Loads toml data to memory.

    Args:
        filename (str): The file name to be loaded
    """
    config_path = Path.home() / "devnetlabs/labs/" / filename
    if not config_path.exists():
        print(f"File '{config_path}' does not exist.")
        return False
    try:
        with open(config_path, "r") as f:
            return toml.load(f)
    except IOError as err:
        print(f"Error loading file '{config_path}': {err}")


def colorme(msg, color):
    """
    Sets the terminal color requested, defaults to white

    Args:
        color (str): Sets the color of text displayed on the terminal
    """
    if color == "red":
        wrapper = "\033[91m"
    elif color == "blue":
        wrapper = "\033[94m"
    elif color == "green":
        wrapper = "\033[92m"
    else:
        # Defaults to white if invalid color is given
        wrapper = "\033[47m"
    return wrapper + msg + "\033[0m"


def clear_screen():
    """
    Runs the terminal clear screen command for the OS in use
    """
    if platform.system().lower() == "windows":
        cmd = "cls"
    else:
        cmd = "clear"
    os.system(cmd)


# https://www.asciiart.eu/text-to-ascii-art
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
