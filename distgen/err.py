import logging
import sys


def fatal(msg, exit_code=1):
    logging.fatal(msg)
    sys.exit(exit_code)
