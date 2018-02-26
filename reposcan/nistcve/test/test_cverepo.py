"""
Unit test classes for repository module.
"""

import unittest
from nistcve.cverepo import CveRepo
from nistcve.cvemeta import CveMeta
from nistcve.cvejson import CveJson

class TestCveRepo(unittest.TestCase):
    """CveRepo test class."""
    def setUp(self):
        """Setup sample cve repo."""
        self.cverepo = CveRepo('modified')
        self.cverepo.json = CveJson("test_data/nistcve/nvdcve-1.0-modified.json")
        self.cverepo.meta = CveMeta("test_data/nistcve/nvdcve-1.0-modified.meta")

    def test_count(self):
        """Test number of CVEs in repo."""
        self.assertEqual(self.cverepo.get_count(), 11)

    def test_list(self):
        """Test list of CVEs in repo."""
        cves = self.cverepo.list_cves()
        self.assertIsInstance(cves, list)
        self.assertEqual(self.cverepo.get_count(), len(cves))

    def test_urls(self):
        """Test repo URLs."""
        self.assertEqual(self.cverepo.meta_url(),
                         "https://static.nvd.nist.gov/feeds/json/cve/1.0/nvdcve-1.0-modified.meta")
        self.assertEqual(self.cverepo.json_url(),
                         "https://static.nvd.nist.gov/feeds/json/cve/1.0/nvdcve-1.0-modified.json.gz")

    def test_tmp(self):
        """Test repo temporary files."""
        self.cverepo.tmp_directory = "/tmp/cve-xyz"
        self.assertEqual(self.cverepo.meta_tmp(), "/tmp/cve-xyz/data.meta")
        self.assertEqual(self.cverepo.json_tmp(), "/tmp/cve-xyz/data.json")
        self.assertEqual(self.cverepo.json_tmpgz(), "/tmp/cve-xyz/data.json.gz")
