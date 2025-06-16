"""
Tests for database upgrade scripts.
"""

import subprocess
import os
import re
import difflib

from vmaas.reposcan.conftest import reset_db
from vmaas.reposcan.database import upgrade

# List of tables whose contents are expected to be stable across upgrades.
STATIC_TABLES = ["db_version", "arch", "arch_compatibility", "errata_severity", "cve_impact", "cve_source", "csaf_product_status"]


def _run_pg_dump(dump_args_in):
    os.environ["PGPASSWORD"] = os.getenv("POSTGRESQL_PASSWORD")
    dump_args = ["pg_dump",
                 "-h", os.getenv("POSTGRESQL_HOST"),
                 "-p", os.getenv("POSTGRESQL_PORT"),
                 "-U", os.getenv("POSTGRESQL_USER"),
                 "-d", os.getenv("POSTGRESQL_DATABASE")]
    dump_args.extend(dump_args_in)
    dump = subprocess.check_output(dump_args).decode("utf-8")
    dump = re.sub(r",?\n+", "\n", dump).splitlines()
    dump.sort()
    return dump


def _dump_database():
    """ Executes the process in args and returns output. """
    dump_schema = _run_pg_dump(["-s"])

    dump_args_data = ["-a"]
    for table_name in STATIC_TABLES:
        dump_args_data.extend(["-t", table_name])
    dump_data = _run_pg_dump(dump_args_data)
    return dump_schema, dump_data


class TestUpgrades:
    """ Tests for checking the upgrades in directory. """

    @staticmethod
    def test_upgrade(db_conn, caplog):
        """Test upgrade process: compare upgraded and from-scratch db."""
        reset_db(db_conn, old_schema=False)
        dump_schema, dump_data = _dump_database()

        reset_db(db_conn, old_schema=True)
        upgrade.main()
        upgraded_dump_schema, upgraded_dump_data = _dump_database()
        try:
            assert dump_schema == upgraded_dump_schema
        except AssertionError:
            diff = difflib.unified_diff(dump_schema, upgraded_dump_schema)
            diffs = "\n".join(list(diff))
            assert False, f"Diffs:\n{diffs}"
        try:
            assert dump_data == upgraded_dump_data
        except AssertionError:
            diff = difflib.unified_diff(dump_data, upgraded_dump_data)
            diffs = "\n".join(list(diff))
            assert False, f"Diffs:\n{diffs}"
        assert "applying upgrade to version 10" in caplog.messages
        assert "upgrade applied successfully" in caplog.messages
