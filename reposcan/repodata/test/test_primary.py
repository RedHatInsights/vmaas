"""
Unit test classes for primary module.
"""
import unittest
from xml.etree.ElementTree import ParseError
from repodata.primary import PrimaryMD


class TestPrimaryMD(unittest.TestCase):
    """Test PrimaryMD class."""
    def setUp(self):
        """Setup example primary file."""
        self.primary = PrimaryMD("test_data/repodata/primary.xml")

    def _test_package(self, pkg):
        intended_fields = ["name", "epoch", "ver", "rel", "arch", "summary", "description"]
        actual_fields = pkg.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)
            self.assertEqual(str, type(pkg[field]))

    def test_invalid_file(self):
        """Test case when file doesn't exist or is invalid."""
        with self.assertRaises(FileNotFoundError):
            PrimaryMD("/file/does/not/exist")
        with self.assertRaises(ParseError):
            PrimaryMD("/dev/null")

    def test_packages(self):
        """Test parsed package metadata fields and counts."""
        pkg_count = self.primary.get_package_count()
        packages = self.primary.list_packages()
        # Package count read from field and number of actually parsed packages should be same
        self.assertEqual(pkg_count, len(packages))
        self.assertEqual(12, pkg_count)
        # Test fields of packages in list
        for pkg in packages:
            self._test_package(pkg)
