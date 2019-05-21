"""SRPM processing functions module."""
import re


class SRPMParseException(Exception):
    """SRPM name parsing exception."""


def parse_srpm_name(name):
    """Extract components from srpm name."""
    # parts = re.search(r'(.*/)*(.*)-(.*)-(.*?)\.(.*)(\.src\.rpm)', name)
    parts = re.search(r'(.*)-(.*)-.+\.src\.rpm', name)
    if parts is None:
        raise SRPMParseException("Failed to parse srpm name!")
    name, ver = parts.groups()
    if name in ["", None]:
        raise SRPMParseException("Empty srpm name found!")
    if ver == ["", None]:
        raise SRPMParseException("Empty srpm evr found!")
    # TODO: make correct parsing
    return name, "0", ver, "fc27"
