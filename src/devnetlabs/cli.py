"""Usage: labs [--version] [-h | --help]"""

import logging

from docopt import docopt

from devnetlabs import labs, utils

logger = logging.getLogger(__name__)


def run():
    """
    Start of application
    """
    utils.setup_environment()
    arguments = docopt(__doc__, version="0.0.0")
    logger.debug(f"Arguments passed in:\n{arguments}")

    logger.info("Starting application")
    labs.main_menu()
