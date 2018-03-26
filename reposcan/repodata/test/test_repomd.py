"""
Unit test classes for repomd module.
"""
from datetime import datetime
import unittest
from xml.etree.ElementTree import ParseError
from repodata.repomd import RepoMD, RepoMDTypeNotFound


class TestRepoMD(unittest.TestCase):
    """Test RepoMD class."""
    def setUp(self):
        """Setup two repomd files. First with all sections. Second with primary section only.
        """
        self.repomd = RepoMD("test_data/repodata/repomd.xml")
        self.repomd_primary_only = RepoMD("test_data/repodata/repomd_primary_only.xml")

    def test_revision(self):
        """Test getting revision timestamp."""
        self.assertIsInstance(self.repomd.get_revision(), datetime)
        self.assertIsInstance(self.repomd_primary_only.get_revision(), datetime)
        self.assertEqual(self.repomd.get_revision(), self.repomd_primary_only.get_revision())

    def _test_repomd(self, data):
        intended_fields = ["location", "size", "checksum_type", "checksum"]
        actual_fields = data.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)

        self.assertIsInstance(data["size"], int)

    def test_invalid_file(self):
        """Test case when file doesn't exist or is invalid."""
        with self.assertRaises(FileNotFoundError):
            RepoMD("/file/does/not/exist")
        with self.assertRaises(ParseError):
            RepoMD("/dev/null")

    def test_get_primary(self):
        """Test getting primary metadata info."""
        primary1 = self.repomd.get_metadata("primary")
        self._test_repomd(primary1)

        primary2 = self.repomd_primary_only.get_metadata("primary")
        self._test_repomd(primary2)

    def test_get_updateinfo(self):
        """Test getting updateinfo metadata info."""
        updateinfo1 = self.repomd.get_metadata("updateinfo")
        self._test_repomd(updateinfo1)

        # Should fail
        with self.assertRaises(RepoMDTypeNotFound):
            self.repomd_primary_only.get_metadata("updateinfo")
