"""Usage: labs [--version] [-h | --help]"""

import logging
import os
from datetime import datetime
from pathlib import Path

from docopt import docopt

# Dynamically create the log filename using current timestamp
logname = f"devnetlabs_{datetime.now():%Y-%m-%d_%H-%M-%S}.log"

# Setup logging directory relative to users home directory
log_path = Path.home() / os.getenv("LABS_LOG_PATH", Path("devnetlabs/logs/"))
log_path.mkdir(parents=True, exist_ok=True)  # Creates directory if not already there

# Check environment variables for log level, defaults to info if none provided
log_level = getattr(logging, os.getenv("LABS_LOG_LEVEL", "info").upper(), None)
if not isinstance(log_level, int):
    raise ValueError("Invalid log level")

# Configure logging
logging.basicConfig(
    filename=log_path / logname,
    encoding="utf-8",
    level=log_level,
    format="%(asctime)s %(filename)14s:%(lineno)s %(levelname)11s > %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


def run():
    arguments = docopt(__doc__, version="0.0.0")
    logging.debug(f"Arguments passed in:\n{arguments}")

