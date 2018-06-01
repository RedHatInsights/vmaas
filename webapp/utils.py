"""
Set of functions and precedures shared between different modules.
"""

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
    return str(datetime_obj)

def parse_datetime(date):
    """Parse date from string in ISO format."""
    if date is None:
        return None
    return dateutil_parser.parse(date)
