#!/usr/bin/env python3
"""
DEPRECATED: keep this file around for some time to delete all generated dumps

Tool for exporting package tree containing CVEs, release date and
channels/streams for use by Product Security.
"""

import glob
from vmaas.common.logging_utils import get_logger, init_logging
from vmaas.common.fileutil import remove_file_if_exists

PKGTREE_FILE = '/data/pkg_tree.json.gz'

LOGGER = get_logger(__name__)


class JsonPkgTree:  # pylint: disable=too-many-instance-attributes
    """Class for creating package tree json file from database."""

    def __init__(self, filename):
        self.filename = filename

    def remove(self):
        """Remove all pkgtree files"""
        old_data = sorted(glob.glob("%s-*" % self.filename), reverse=True)
        for fname in old_data:
            LOGGER.info("Removing old dump %s", fname)
            remove_file_if_exists(fname)
        remove_file_if_exists(self.filename)


def main(filename):
    """ Main loop."""
    init_logging()
    data = JsonPkgTree(filename)
    data.remove()


if __name__ == '__main__':
    main(PKGTREE_FILE)
