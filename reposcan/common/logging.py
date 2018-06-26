"""
Module containing helper functions to setup and get logging objects.
"""
import os
import logging


def init_logging():
    """Setup root logger handler."""
    logger = logging.getLogger()
    uuid = os.uname().nodename
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter(fmt=uuid + " %(asctime)s %(name)s: [%(levelname)s] %(message)s"))
        logger.addHandler(handler)


def get_logger(name):
    """
    Set logging level and return logger.
    Don't set custom logging level in root handler to not display debug messages from underlying libraries.
    """
    logger = logging.getLogger(name)
    level = os.getenv('LOGGING_LEVEL', "INFO")
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger
