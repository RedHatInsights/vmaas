"""
Set of functions and procedures shared between different modules.
"""

import math
import re
from datetime import datetime

import rpm
from dateutil import parser as dateutil_parser

from vmaas.common.rpm_utils import join_rpm_name, parse_rpm_name

PKG_NAME_ID = 0
PKG_EVR_ID = 1
PKG_ARCH_ID = 2


def pkg_detail2nevra(cache, pkg_detail):
    """Create package object from pkg_detail using cache object."""
    name = cache.id2packagename[pkg_detail[PKG_NAME_ID]]
    epoch, ver, rel = cache.id2evr[pkg_detail[PKG_EVR_ID]]
    arch = cache.id2arch[pkg_detail[PKG_ARCH_ID]]
    return join_rpm_name(name, epoch, ver, rel, arch)


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
def paginate(input_list, page, page_size, filters=None, sort_input=True):
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

    if sort_input:
        input_list.sort()
    if filters:
        for filter_method, filter_args in filters:
            input_list = filter_method(*[input_list, *filter_args])
    start = (page - 1) * page_size
    end = page * page_size
    pages = int(math.ceil(float(len(input_list))/page_size))
    result_list = input_list[start:end]
    return result_list, {"page": page, "page_size": len(result_list), "pages": pages}


def filter_item_if_exists(list_to_process, item_details):
    """
    Filter to check if item exists
    :param item_details: item details from cache
    :param list_to_process: list of items to filter
    :return: filtered list of items
    """

    filtered_list_to_process = []
    for item in list_to_process:
        item_detail = item_details.get(item)
        if item_detail:
            filtered_list_to_process.append(item)
    return filtered_list_to_process


def filter_package_list(package_list, latest_only=False):
    """
    Filter packages with latest NEVRA
    :param package_list: list of package NEVRAs
    :param latest_only: boolean switch to return only latest NEVRA for given name.arch
    :return: filtered list of NEVRAs
    """
    if not latest_only:
        return package_list
    latest_pkgs = {}
    for pkg in package_list:
        name, epoch, ver, rel, arch = parse_rpm_name(pkg)
        if (name, arch) in latest_pkgs:
            latest = latest_pkgs[(name, arch)][0:3]
            if rpm.labelCompare((epoch, ver, rel), latest) < 1: # pylint: disable=no-member
                continue
        latest_pkgs[(name, arch)] = (epoch, ver, rel, pkg)
    return [val[3] for val in latest_pkgs.values()]


def find_by_regex(regex: str, labeled_data: dict) -> list:
    """Returns list of matching labels for provided regex."""
    if not regex.startswith('^'):
        regex = '^' + regex

    if not regex.endswith('$'):
        regex = regex + '$'

    matching_data = [label for label in labeled_data if re.match(regex, label)]
    return matching_data


def try_expand_by_regex(input_labels: list, labeled_data: dict) -> list:
    """Treat single-label like a regex, get all matching names"""
    if len(input_labels) == 1:
        output_labels = find_by_regex(regex=input_labels[0], labeled_data=labeled_data)
        if len(output_labels) > 0:
            return output_labels
    return input_labels


def strip_prefixes(repos: list, prefixes: list):
    """Strips prefixes from repo names"""
    for i, repo in enumerate(list(repos)):
        for prefix in prefixes:
            if repo.startswith(prefix):
                repos[i] = repo[len(prefix):]
                break
