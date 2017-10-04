import logging
import sys


def fatal(msg):
    logging.fatal(msg)
    sys.exit(1)
