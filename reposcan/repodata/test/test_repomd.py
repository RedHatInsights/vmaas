import unittest
from xml.etree.ElementTree import ParseError
from repodata.repomd import RepoMD, RepoMDTypeNotFound


class TestRepoMD(unittest.TestCase):
    def setUp(self):
        """Setup two repomd files. First with all sections. Second with primary section only.
        """
        self.repomd = RepoMD("test_data/repodata/repomd.xml")
        self.repomd_primary_only = RepoMD("test_data/repodata/repomd_primary_only.xml")

    def _test_repomd(self, md):
        intended_fields = ["location", "size", "checksum_type", "checksum"]
        actual_fields = md.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)

        self.assertIsInstance(md["size"], int)

    def test_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            RepoMD("/file/does/not/exist")
        with self.assertRaises(ParseError):
            RepoMD("/dev/null")

    def test_get_primary(self):
        primary1 = self.repomd.get_metadata("primary")
        self._test_repomd(primary1)

        primary2 = self.repomd_primary_only.get_metadata("primary")
        self._test_repomd(primary2)

    def test_get_updateinfo(self):
        updateinfo1 = self.repomd.get_metadata("updateinfo")
        self._test_repomd(updateinfo1)

        # Should fail
        with self.assertRaises(RepoMDTypeNotFound):
            self.repomd_primary_only.get_metadata("updateinfo")
