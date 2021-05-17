"""
Tests for database upgrade scripts.
"""

import subprocess
import os
import re
import difflib
import pytest
from git import Repo
from vmaas.reposcan.database.test.conftest import create_pg, VMAAS_DIR

# pylint: disable=no-self-use
# pylint: disable=unnecessary-comprehension

UPGRADE_FROM = os.getenv("UPGRADE_FROM", "d5ce37e4b9ae8fd93adab80946ede0e36f5a5565")
UPGRADE_TO = os.getenv("UPGRADE_TO", None)

STATIC_TABLES = ["db_version"]

def _dump_database(args):
    """ Executes the process in args and returns output. """
    dump = subprocess.check_output(args).decode("utf-8")
    dump = re.sub(r",?\n+", "\n", dump).splitlines()
    dump.sort()
    return dump


class TestUpgrades:
    """ Tests for checking the upgrades in directory. """
    repo = Repo(VMAAS_DIR)

    if repo.head.is_detached:
        head = repo.create_head(repo.head.commit.name_rev[:7], commit=repo.head.commit.hexsha)
    else:
        head = repo.head.reference

    def _git_checkout(self, commit):
        """ Perform git checkout specified by commit and stash current work. """
        stashed = False
        if self.repo.is_dirty():
            self.repo.git.stash()
            stashed = True

        self.repo.head.reference = self.head
        if commit:
            self.repo.head.reference = self.repo.create_head(commit[:7], commit=commit)
        self.repo.head.reset(index=True, working_tree=True)
        return stashed

    def _git_co_teardown(self, commit, stashed):
        """ Performs teardown of git changes. """
        self.repo.head.reference = self.head
        self.repo.head.reset(index=True, working_tree=True)
        if commit:
            self.repo.delete_head(commit[:7], force=True)
        if stashed:
            self.repo.git.stash("pop")

    @pytest.fixture(autouse=True)
    def teardown(self):
        """ Teardown for tests, saves the enviroment vars. """
        enviroment = dict(os.environ)
        os.environ.clear()
        yield
        os.environ.clear()
        os.environ.update(enviroment)

    @pytest.fixture
    def pg_old(self, commit=UPGRADE_FROM):
        """Setup DB with old schema."""
        stashed = self._git_checkout(commit)
        pg_instance = create_pg()

        yield pg_instance

        pg_instance.stop()
        self._git_co_teardown(commit, stashed)

    @pytest.fixture
    def pg_new(self, commit=UPGRADE_TO):
        """Setup DB with new schema."""
        stashed = self._git_checkout(commit)
        pg_instance = create_pg()

        yield pg_instance

        pg_instance.stop()
        self._git_co_teardown(commit, stashed)

    def test_upgrade(self, pg_old, pg_new):
        """ Test the upgrades in folders. """
        dsn_old = pg_old.dsn()
        dsn_new = pg_new.dsn()

        os.environ["POSTGRESQL_DATABASE"] = str(dsn_old["database"])
        os.environ["POSTGRESQL_USER"] = str(dsn_old["user"])
        os.environ["POSTGRESQL_HOST"] = str(dsn_old["host"])
        os.environ["POSTGRESQL_PORT"] = str(dsn_old["port"])

        # pylint: disable=import-outside-toplevel
        from vmaas.reposcan.database import upgrade
        upgrade.main()

        schema_old_args = [
            "pg_dump", "-s",
            "-h", str(dsn_old["host"]),
            "-p", str(dsn_old["port"]),
            "-U", str(dsn_old["user"]),
            "-d", str(dsn_old["database"])
        ]

        schema_new_args = [
            "pg_dump", "-s",
            "-h", str(dsn_new["host"]),
            "-p", str(dsn_new["port"]),
            "-U", str(dsn_new["user"]),
            "-d", str(dsn_new["database"])
        ]

        dump_old = _dump_database(schema_old_args)
        dump_new = _dump_database(schema_new_args)

        try:
            assert dump_old == dump_new
        except AssertionError:
            diff = difflib.unified_diff(dump_old, dump_new)
            diffs = "\n".join([x for x in diff])
            assert False, f"Diffs:\n{diffs}"

        data_args = ["pg_dump", "-a"]
        for table in STATIC_TABLES:
            data_args.append("-t")
            data_args.append(table)

        data_old_args = data_args + [
            "-h", str(dsn_old["host"]),
            "-p", str(dsn_old["port"]),
            "-U", str(dsn_old["user"]),
            "-d", str(dsn_old["database"])
        ]

        data_new_args = data_args + [
            "-h", str(dsn_new["host"]),
            "-p", str(dsn_new["port"]),
            "-U", str(dsn_new["user"]),
            "-d", str(dsn_new["database"])
        ]

        old_data_dump = _dump_database(data_old_args)
        new_data_dump = _dump_database(data_new_args)

        try:
            assert old_data_dump == new_data_dump
        except AssertionError:
            diff = difflib.unified_diff(old_data_dump, new_data_dump)
            diffs = "\n".join([x for x in diff])
            assert False, f"Diff:\n{diffs}"
