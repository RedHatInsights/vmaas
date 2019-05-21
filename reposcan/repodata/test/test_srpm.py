"""
Unit test classes for srpm module.
"""
import unittest

from repodata import srpm


class TestSrpm(unittest.TestCase):
    """Test srpm module functions"""

    def test_parse_1(self):
        """Test parsing valid srpm name."""
        name, _, ver, _ = srpm.parse_srpm_name('389-ds-base-1.3.7.8-1.fc27.src.rpm')
        self.assertEqual("389-ds-base", name)
        self.assertEqual("1.3.7.8", ver)

    def test_parse_2(self):
        """Test parsing invalid srpm name."""
        with self.assertRaises(srpm.SRPMParseException):
            srpm.parse_srpm_name('fake.src.rpm')
