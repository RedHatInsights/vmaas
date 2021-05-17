"""
Unit test classes for primary_db module.
"""
from sqlite3 import OperationalError
from vmaas.reposcan.repodata.primary_db import PrimaryDatabaseMD

from vmaas.reposcan.repodata.test.test_primary import TestPrimaryMD


class TestPrimaryDatabaseMD(TestPrimaryMD):
    """Test PrimaryDatabaseMD class."""
    def setUp(self):
        """Setup example primary_db file."""
        self.primary_db = PrimaryDatabaseMD("test_data/repodata/primary_db.sqlite")

    def test_invalid_file(self):
        """Test case when file doesn't exist or is invalid."""
        with self.assertRaises(OperationalError):
            PrimaryDatabaseMD("/file/does/not/exist")
            PrimaryDatabaseMD("/dev/null")

    def test_packages(self):
        """Test parsed package metadata fields and counts."""
        self.assertGreater(self.primary_db.get_package_count(), 0)
        packages = self.primary_db.list_packages()
        # Test fields of packages in list
        for pkg in packages:
            self._test_package(pkg)
