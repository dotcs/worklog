import logging
import sys

import worklog.constants as wc


def configure_logger() -> logging.Logger:
    logger = logging.getLogger(wc.DEFAULT_LOGGER_NAME)
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(wc.LOG_FORMAT)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger
