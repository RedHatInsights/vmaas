"""SRPM processing functions module."""

import re


class RPMParseException(Exception):
    """SRPM name parsing exception."""


def parse_rpm_name(name):
    """Extract components from rpm name."""
    parts = re.search(r'((.*):)?(.*)-(.*)-(.*)\.(.*)\.rpm', name)
    if parts is None:
        raise RPMParseException("Failed to parse srpm name!")
    grps = parts.groups()
    _, epoch, name, ver, rel, arch = grps
    if epoch is None:
        epoch = "0"
    return name, epoch, ver, rel, arch
