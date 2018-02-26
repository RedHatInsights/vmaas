"""
Unit test classes for CveJson module.
"""
import unittest
from nistcve.cvejson import CveJson

class TestCveJson(unittest.TestCase):
    """Test CveJson class."""
    def setUp(self):
        """Setup sample CveJson object."""
        self.json = CveJson("test_data/nistcve/nvdcve-1.0-modified.json")

    def test_count(self):
        """Test number of CVEs in json."""
        self.assertEqual(self.json.get_count(), 11)

    def test_list(self):
        """Test list of CVEs in json."""
        cves = self.json.list_cves()
        self.assertIsInstance(cves, list)
        self.assertEqual(self.json.get_count(), len(cves))
