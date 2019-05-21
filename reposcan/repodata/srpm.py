"""SRPM processing functions module."""


# src: https://github.com/rpm-software-management/yum/blob/master/rpmUtils/miscutils.py
def parse_srpm_name(filename):
    """
    Pass in a standard style rpm fullname

    Return a name, version, release, epoch, arch, e.g.::
        foo-1.0-1.i386.rpm returns foo, 1.0, 1, i386
        1:bar-9-123a.ia64.rpm returns bar, 9, 123a, 1, ia64
    """

    if filename[-4:] == '.rpm':
        filename = filename[:-4]

    arch_index = filename.rfind('.')
    arch = filename[arch_index + 1:]

    rel_index = filename[:arch_index].rfind('-')
    rel = filename[rel_index + 1:arch_index]

    ver_index = filename[:rel_index].rfind('-')
    ver = filename[ver_index + 1:rel_index]

    epoch_index = filename.find(':')
    if epoch_index == -1:
        epoch = "0"
    else:
        epoch = filename[:epoch_index]

    name = filename[epoch_index + 1:ver_index]
    return name, epoch, ver, rel, arch
