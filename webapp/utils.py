"""
Set of functions and procedures shared between different modules.
"""

import math
import re
from datetime import datetime
from dateutil import parser as dateutil_parser

from cache import PKG_NAME_ID, PKG_EVR_ID, PKG_ARCH_ID


def join_packagename(name, epoch, version, release, arch):
    """
    Build a package name from the separate NEVRA parts
    """
    epoch = ("%s:" % epoch) if int(epoch) else ''
    return "%s-%s%s-%s.%s" % (name, epoch, version, release, arch)


def pkg_detail2nevra(cache, pkg_detail):
    """Create package object from pkg_detail using cache object."""
    name = cache.id2packagename[pkg_detail[PKG_NAME_ID]]
    epoch, ver, rel = cache.id2evr[pkg_detail[PKG_EVR_ID]]
    arch = cache.id2arch[pkg_detail[PKG_ARCH_ID]]
    return join_packagename(name, epoch, ver, rel, arch)


def pkgidlist2packages(cache, pkgid_list):
    """
    This method returns a two lists of package-nevras for the given list of package ids from
    the specified cache. 1 - binary packages list, 2 - source packages list
    """
    pkg_list = []
    source_pkg_list = []
    src_arch_id = cache.arch2id["src"]
    for pkg_id in pkgid_list:
        pkg_detail = cache.package_details[pkg_id]
        pkg_str = pkg_detail2nevra(cache, pkg_detail)
        if pkg_detail[PKG_ARCH_ID] == src_arch_id:
            source_pkg_list.append(pkg_str)
        else:
            pkg_list.append(pkg_str)
    return pkg_list, source_pkg_list


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
def paginate(input_list, page, page_size, filters=None):
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
    if filters:
        for filter_method, filter_args in filters:
            input_list = filter_method(*[input_list, *filter_args])
    start = (page - 1) * page_size
    end = page * page_size
    pages = int(math.ceil(float(len(input_list))/page_size))
    result_list = input_list[start:end]
    return (result_list, {"page": page, "page_size": len(result_list), "pages": pages})
