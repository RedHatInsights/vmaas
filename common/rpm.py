"""
SRPM processing functions module.
"""

import re


class RPMParseException(Exception):
    """
    SRPM name parsing exception.
    """

# This will parse package names in the following formats:
# 389-ds-base-1.3.7.8-1.fc27.src
# perl-DBD-Pg-2:3.7.4-2.module+el8+2517+b1471f1c.x86_64
# 3:Agda-2.5.2-9.fc27.x86_64
# Note the epoch can be in either of two locations, or not
# present at all.
NEVRA_RE = re.compile(
    r'((?P<e1>[0-9]+):)?(?P<pn>[^:]+)(?(e1)-|-((?P<e2>[0-9]+):)?)(?P<ver>[^-:]+)-(?P<rel>[^-:]+)\.(?P<arch>[a-z0-9_]+)')

def parse_rpm_name(rpm_name, default_epoch=None, raise_exception=False):
    """
    Extract components from rpm name.
    """
    filename = rpm_name
    if rpm_name[-4:] == '.rpm':
        filename = rpm_name[:-4]

    match = NEVRA_RE.match(filename)
    if not match:
        if raise_exception:
            raise RPMParseException("Failed to parse rpm name '%s'!" % rpm_name)
        return ('', default_epoch, '', '', '')

    name = match.group('pn')
    epoch = match.group('e1')
    if not epoch:
        epoch = match.group('e2')
    if not epoch:
        epoch = default_epoch
    version = match.group('ver')
    release = match.group('rel')
    arch = match.group('arch')
    return name, epoch, version, release, arch

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
