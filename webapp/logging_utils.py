"""
Common logging functionality to be used for multiple apps
(should be identical to reposcan/common/logging.py)
TODO: packaging changes that let this live in one place please
"""

import logging
import os

class OneLineExceptionFormatter(logging.Formatter):
    """
    Formatter used to insure each log-entry is one line
    (insures one entry-per-log for some logging environments that divide on newline)
    """

    # pylint: disable=arguments-differ
    def formatException(self, exc_info):
        """
        Make sure exception-tracebacks end up on a single line.
        """
        result = super(OneLineExceptionFormatter, self).formatException(exc_info)
        return repr(result)

    def format(self, record):
        """
        Convert newlines in each record to |
        """
        fmt_str = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            fmt_str = fmt_str.replace('\n', '') + '|'
        return fmt_str

def init_logging(num_servers=1):
    """Setup root logger handler."""
    logger = logging.getLogger()
    log_type = os.getenv('LOGGING_TYPE', "OPENSHIFT")
    if log_type == "OPENSHIFT":
        log_fmt = "%(name)s: [%(levelname)s] %(message)s"
    else:
        uuid = os.uname().nodename
        if num_servers > 1:
            uuid += ":%d" % os.getpid()
        log_fmt = uuid + " %(asctime)s %(name)s: [%(levelname)s] %(message)s"
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = OneLineExceptionFormatter(log_fmt)
        handler.setFormatter(formatter)
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
