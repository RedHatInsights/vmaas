"""
Unit test classes for cvemeta module.
"""

import unittest
from nistcve.cvemeta import CveMeta

class TestCveMeta(unittest.TestCase):
    """Test CveMeta class."""
    def setUp(self):
        """Setup sample CveMeta object."""
        self.meta = CveMeta("test_data/nistcve/nvdcve-1.0-modified.meta")

    def test_lastmodified(self):
        """Test parsing lastmodified from meta file."""
        self.assertEqual(self.meta.get_lastmodified(), "2018-02-24T20:01:42-05:00")

    def test_sha256(self):
        """Test parsing checksum from meta file."""
        self.assertEqual(self.meta.get_sha256(),
                         "BF7EB68FF86D7AE4C16BAFE9BA6F392526378F9595808D4C7EE1223F4DF23FC0")
