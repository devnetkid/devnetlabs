"""Usage:

    jlabs
    jlabs -h | --help | --version

"""

import logging

from docopt import docopt


def run():
    arguments = docopt(__doc__, version='0.0.0')
    print(arguments)
