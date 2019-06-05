"""
SRPM processing functions module.
"""

import re


class RPMParseException(Exception):
    """
    SRPM name parsing exception.
    """


def parse_rpm_name(name):
    """
    Extract components from rpm name.
    """

    parts = re.search(r'((.*):)?(.*)-(.*)-(.*)\.(.*)\.rpm', name)
    if parts is None:
        raise RPMParseException("Failed to parse srpm name!")
    grps = parts.groups()
    _, epoch, name, ver, rel, arch = grps
    if epoch is None:
        epoch = "0"
    return name, epoch, ver, rel, arch


def rpmver2array(rpm_version: str) -> list:
    """
    Convert RPM version string to comparable array
    of (num, word) tuples.
    Example: '1a' -> [(1,''),(0,'a'),(-2,'')]
    """

    parsed_arr = re.findall(r"(~*)(([A-Za-z]+)|(\d+))(\^*)",
                            rpm_version)  # parse all letters and digits with or without ~ or ^ to
    arr = []
    for til, _, word, num_str, cir in parsed_arr:
        if til != '':
            num = -2              # set num lower if it's after "~" than default (-1)
        elif num_str != '':
            num = int(num_str)    # use parsed number if found
        else:
            num = 0               # for letter-only member set num to zero

        arr.append((num, word))
        if cir != '':
            arr.append((-1, ''))  # if circumflex found, append one member between zero and default (-2)
    arr.append((-2, ''))          # fill array to "n_len"
    return arr


def rpmver2sqlarray(rpm_version: str) -> str:
    """
    Convert rpm version string to comparable SQL array string.
    Example: '1a' -> {"(1,)","(0,a)","(-2,)"}
    """

    arr = rpmver2array(rpm_version)
    sarr = []  # create array from sql syntax elements
    for num_str, word in arr:
        str_elem = '"(%d,%s)"' % (num_str, word)
        sarr.append(str_elem)
    res = '{%s}' % ','.join(sarr)
    return res
