"""
Set of functions and precedures shared between different modules.
"""

def join_packagename(name, epoch, version, release, arch):
    """
    Build a package name from the separate NEVRA parts
    """
    epoch = str(epoch) + ':' if int(epoch) else ''
    return "%s-%s%s-%s.%s" % (name, epoch, version, release, arch)
