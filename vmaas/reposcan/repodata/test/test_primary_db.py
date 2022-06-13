"""
Unit test classes for primary_db module.
"""
# pylint: disable=no-self-use
from sqlite3 import OperationalError
import pytest
from vmaas.reposcan.repodata.primary_db import PrimaryDatabaseMD

from vmaas.reposcan.repodata.test.test_primary import TestPrimaryMD


class TestPrimaryDatabaseMD(TestPrimaryMD):
    """Test PrimaryDatabaseMD class."""

    def test_invalid_file(self):
        """Test case when file doesn't exist or is invalid."""
        with pytest.raises(OperationalError):
            PrimaryDatabaseMD("/file/does/not/exist")
            PrimaryDatabaseMD("/dev/null")

    def test_packages(self):
        """Test parsed package metadata fields and counts."""
        primary_db = PrimaryDatabaseMD("test_data/repodata/primary_db.sqlite")
        assert primary_db.get_package_count() > 0
        packages = primary_db.list_packages()
        # Test fields of packages in list
        for pkg in packages:
            self._test_package(pkg)
