import unittest
from sqlite3 import OperationalError
from repodata.primary_db import PrimaryDatabaseMD


class TestPrimaryDatabaseMD(unittest.TestCase):
    def setUp(self):
        """Setup example primary_db file."""
        self.primary_db = PrimaryDatabaseMD("test_data/repodata/primary_db.sqlite")

    def _test_package(self, pkg):
        intended_fields = ["name", "epoch", "ver", "rel", "arch", "checksum_type", "checksum"]
        actual_fields = pkg.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)

    def test_invalid_file(self):
        with self.assertRaises(OperationalError):
            PrimaryDatabaseMD("/file/does/not/exist")
            PrimaryDatabaseMD("/dev/null")

    def test_packages(self):
        self.assertGreater(self.primary_db.get_package_count(), 0)
        packages = self.primary_db.list_packages()
        # Test fields of packages in list
        for pkg in packages:
            self._test_package(pkg)
