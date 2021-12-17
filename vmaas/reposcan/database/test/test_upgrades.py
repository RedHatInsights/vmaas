"""
Tests for database upgrade scripts.
"""

import subprocess
import os
import re
import difflib

from vmaas.reposcan.conftest import reset_db
from vmaas.reposcan.database import upgrade


def _dump_database():
    """ Executes the process in args and returns output. """
    os.environ["PGPASSWORD"] = os.getenv("POSTGRESQL_PASSWORD")
    dump_args = ["pg_dump", "-s",
                 "-h", os.getenv("POSTGRESQL_HOST"),
                 "-p", os.getenv("POSTGRESQL_PORT"),
                 "-U", os.getenv("POSTGRESQL_USER"),
                 "-d", os.getenv("POSTGRESQL_DATABASE")]

    dump = subprocess.check_output(dump_args).decode("utf-8")
    dump = re.sub(r",?\n+", "\n", dump).splitlines()
    dump.sort()
    return dump


class TestUpgrades:
    """ Tests for checking the upgrades in directory. """

    @staticmethod
    def test_upgrade(db_conn, caplog):
        """Test upgrade process: compare upgraded and from-scratch db."""
        reset_db(db_conn, old_schema=False)
        dump = _dump_database()

        reset_db(db_conn, old_schema=True)
        upgrade.main()
        upgraded_dump = _dump_database()
        try:
            assert dump == upgraded_dump
        except AssertionError:
            diff = difflib.unified_diff(dump, upgraded_dump)
            diffs = "\n".join(list(diff))
            assert False, f"Diffs:\n{diffs}"
        assert "applying upgrade to version 10" in caplog.messages
        assert "upgrade applied successfully" in caplog.messages
