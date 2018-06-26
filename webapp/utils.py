"""
Set of functions and precedures shared between different modules.
"""

import logging
import math
import os
import re
from datetime import datetime
from dateutil import parser as dateutil_parser

def join_packagename(name, epoch, version, release, arch):
    """
    Build a package name from the separate NEVRA parts
    """
    epoch = ("%s:" % epoch) if int(epoch) else ''
    return "%s-%s%s-%s.%s" % (name, epoch, version, release, arch)

NEVRA_RE = re.compile(r'(.*)-(([0-9]+):)?([^-]+)-([^-]+)\.([a-z0-9_]+)')
def split_packagename(filename):
    """
    Split rpm name (incl. epoch) to NEVRA components.

    Return a name, epoch, version, release, arch, e.g.::
        foo-1.0-1.i386.rpm returns foo, 0, 1.0, 1, i386
        bar-1:9-123a.ia64.rpm returns bar, 1, 9, 123a, ia64
    """

    if filename[-4:] == '.rpm':
        filename = filename[:-4]

    match = NEVRA_RE.match(filename)
    if not match:
        return '', '', '', '', ''

    name, _, epoch, version, release, arch = match.groups()
    if epoch is None:
        epoch = '0'
    return name, epoch, version, release, arch


def format_datetime(datetime_obj):
    """Try to format object to ISO 8601 if object is datetime."""
    if isinstance(datetime_obj, datetime):
        return datetime_obj.isoformat()
    return None if datetime_obj is None else str(datetime_obj)

def parse_datetime(date):
    """Parse date from string in ISO format."""
    if date is None:
        return None
    ret = dateutil_parser.parse(date)
    if not ret.tzinfo:
        raise ValueError("Wrong date format (not ISO format with timezone): " + date)
    return ret

def none2empty(value):
    """Convert None to empty string."""
    return value if value is not None else ""

DEFAULT_PAGE = 1
DEFAULT_PAGE_SIZE = 5000
def paginate(input_list, page, page_size):
    """Split input list into pages and return only requested page."""
    def _validate_num(num, default):
        try:
            num = int(num)
            if num <= 0:
                num = default
        except (TypeError, ValueError):
            num = default
        return num

    page = _validate_num(page, DEFAULT_PAGE)
    page_size = _validate_num(page_size, DEFAULT_PAGE_SIZE)

    input_list.sort()
    start = (page - 1) * page_size
    end = page * page_size
    pages = int(math.ceil(float(len(input_list))/page_size))
    return (input_list[start:end], {"page": page, "page_size": page_size, "pages": pages})

def init_logging(num_servers=1):
    """Setup root logger handler."""
    logger = logging.getLogger()
    uuid = os.uname().nodename
    if num_servers > 1:
        uuid += ":%d" % os.getpid()
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
