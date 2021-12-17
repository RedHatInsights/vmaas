"""
Unit test classes for pkgtree module.
"""
# pylint: disable=no-self-use

import gzip
import json

from vmaas.reposcan.pkgtree import JsonPkgTree
from vmaas.reposcan.conftest import write_testing_data

TEST_DUMP_FILE = "/tmp/dump.output"


class TestPkgtree:
    """Test Exporter class."""

    def test_dump(self, db_conn):
        """Test pkgtree dump."""
        write_testing_data(db_conn)
        ddump = JsonPkgTree(db_conn, TEST_DUMP_FILE)
        ddump.dump()
        with gzip.open(TEST_DUMP_FILE) as dumpfile:
            pkgtree = json.load(dumpfile)
            # from IPython import embed; embed()

            self.check_timestamp(pkgtree)
            self.check_packages(pkgtree)

    @staticmethod
    def check_timestamp(pkgtree: dict):
        """Check timestamp field."""
        assert pkgtree["timestamp"] is not None

    @staticmethod
    def check_packages(pkgtree: dict):
        """Check packages field."""
        assert len(pkgtree["packages"]) == 4
