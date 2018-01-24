import unittest
from xml.etree.ElementTree import ParseError
from repodata.primary import PrimaryMD


class TestPrimaryMD(unittest.TestCase):
    def setUp(self):
        """Setup example primary file."""
        self.primary = PrimaryMD("test_data/repodata/primary.xml")

    def _test_package(self, pkg):
        intended_fields = ["name", "epoch", "ver", "rel", "arch", "checksum_type", "checksum"]
        actual_fields = pkg.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)

    def test_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            PrimaryMD("/file/does/not/exist")
        with self.assertRaises(ParseError):
            PrimaryMD("/dev/null")

    def test_packages(self):
        pkg_count = self.primary.get_package_count()
        packages = self.primary.list_packages()
        # Package count read from field and number of actually parsed packages should be same
        self.assertEqual(pkg_count, len(packages))
        # Test fields of packages in list
        for pkg in packages:
            self._test_package(pkg)
