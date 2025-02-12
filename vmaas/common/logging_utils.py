"""
Common logging functionality to be used for multiple apps
(should be identical to reposcan/common/logging.py)
TODO: packaging changes that let this live in one place please
"""
import json
import logging
import os
import time
from threading import Lock

import watchtower
from boto3 import client
from botocore.exceptions import ClientError

from vmaas.common.config import Config
from vmaas.common.strtobool import strtobool


class OneLineExceptionFormatter(logging.Formatter):
    """
    Formatter used to insure each log-entry is one line
    (insures one entry-per-log for some logging environments that divide on newline)
    """

    # pylint: disable=arguments-differ, arguments-renamed
    def formatException(self, exc_info):
        """
        Make sure exception-tracebacks end up on a single line.
        """
        result = super().formatException(exc_info)
        return repr(result)

    def format(self, record):
        """
        Convert newlines in each record to |
        """
        fmt_str = super().format(record)
        if record.exc_text:
            fmt_str = fmt_str.replace('\n', '') + '|'
        return fmt_str


class CloudWatchLogFormatterCustom(watchtower.CloudWatchLogFormatter):
    """
    Formatter used for loging in CloudWatch.
    Compared to CloudWatchLogFormatter it formats string arguments in the message when the message is JSON.
    """

    def format(self, message):
        """
        Include level name and dump as JSON.
        """
        formatted_message = logging.Formatter.format(self, message)
        msg = {"levelname": getattr(message, "levelname"), "message": formatted_message}
        return json.dumps(msg, default=self.json_serialize_default)


def setup_cw_logging(main_logger):
    """Setup CloudWatch logging"""
    logger = get_logger(__name__)
    cfg = Config()
    if not strtobool(os.getenv('CW_ENABLED', 'FALSE')):
        logger.info('CloudWatch logging disabled')
        return
    key_id = cfg.cw_aws_access_key_id
    secret = cfg.cw_aws_secret_access_key
    if not (key_id and secret):
        logger.info('CloudWatch logging disabled due to missing access key')
        return

    boto3_client = client(
        "logs",
        aws_access_key_id=key_id,
        aws_secret_access_key=secret,
        region_name=cfg.cw_aws_region
    )

    try:
        handler = watchtower.CloudWatchLogHandler(
            boto3_client=boto3_client,
            log_group=cfg.cw_aws_log_group,
            stream_name=os.environ.get('HOSTNAME', 'vmaas')
        )
        handler.setFormatter(CloudWatchLogFormatterCustom())
    except ClientError:
        logger.exception("Unable to enable CloudWatch logging: ")
    else:  # pragma: no cover
        main_logger.addHandler(handler)
        logger.info('CloudWatch logging ENABLED!')


class ProgressLogger:
    """
    Class to log progress every N seconds.
    """

    def __init__(self, logger, total, log_interval=60):
        self.logger = logger
        self.log_interval = log_interval
        self.total = total
        self.lock = Lock()
        self.last_log_time = 0
        self.completed = 0

    def reset(self, total):
        """Initialize all counters."""
        with self.lock:
            self.total = total
            self.last_log_time = 0
            self.completed = 0

    def get_completed_percent(self):
        """Get percentage of completed items."""
        return round(((self.completed / self.total) * 100), 2)

    def update(self, source=None, target=None):
        """
        One item was completed. Log it if N seconds since last log passed.
        And log every update on debug level.
        """
        with self.lock:
            self.completed += 1
            now = time.time()
            if (now - self.last_log_time) > self.log_interval or self.completed == self.total:
                self.logger.info("%6.2f %% completed [%s/%s]", self.get_completed_percent(),
                                 self.completed, self.total)
                self.last_log_time = now
            if source and target:
                self.logger.debug("[%s/%s] %s -> %s", self.completed, self.total, source, target)


def init_logging(num_servers=1):
    """Setup root logger handler."""
    logger = logging.getLogger()
    log_type = os.getenv('LOGGING_TYPE', "OPENSHIFT")
    log_fmt = "%(asctime)s:%(levelname)s:%(name)s:%(message)s"
    if log_type != "OPENSHIFT":
        uuid = os.uname().nodename
        if num_servers > 1:
            uuid += ":%d" % os.getpid()
        log_fmt = "%s %s" % (uuid, log_fmt)
    level = os.getenv('LOGGING_LEVEL_LIBS', "WARNING")
    logger.setLevel(getattr(logging, level, logging.WARNING))
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = OneLineExceptionFormatter(log_fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        setup_cw_logging(logger)


def get_logger(name: str) -> logging.Logger:
    """
    Set logging level and return logger.
    Don't set custom logging level in root handler to not display debug messages from underlying libraries.
    """
    logger = logging.getLogger(name)
    level = os.getenv('LOGGING_LEVEL_APP', "INFO")
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger
