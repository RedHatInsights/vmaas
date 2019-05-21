"""
Unit test classes for srpm module.
"""
import unittest

from repodata import srpm


class TestSrpm(unittest.TestCase):
    """Test srpm module functions"""

    def test_parse_1_srpm(self):
        """Test parsing valid srpm name."""
        name, epoch, ver, rel, arch = srpm.parse_rpm_name('389-ds-base-1.3.7.8-1.fc27.src.rpm')
        self.assertEqual("0", epoch)
        self.assertEqual("389-ds-base", name)
        self.assertEqual("1.3.7.8", ver)
        self.assertEqual("1.fc27", rel)
        self.assertEqual("src", arch)

    def test_parse_2_rpm(self):
        """Test parsing valid rpm name."""
        name, epoch, ver, rel, arch = srpm.parse_rpm_name('Agda-2.5.2-9.fc27.x86_64.rpm')
        self.assertEqual("0", epoch)
        self.assertEqual("Agda", name)
        self.assertEqual("2.5.2", ver)
        self.assertEqual("9.fc27", rel)
        self.assertEqual("x86_64", arch)

    def test_parse_3_epoch(self):
        """Test parsing valid rpm name with epoch."""
        name, epoch, ver, rel, arch = srpm.parse_rpm_name('3:Agda-2.5.2-9.fc27.x86_64.rpm')
        self.assertEqual("3", epoch)
        self.assertEqual("Agda", name)
        self.assertEqual("2.5.2", ver)
        self.assertEqual("9.fc27", rel)
        self.assertEqual("x86_64", arch)

    def test_parse_4_invalid_rpmname(self):
        """Test parsing invalid rpm name."""
        with self.assertRaises(srpm.RPMParseException):
            srpm.parse_rpm_name('foo')
        with self.assertRaises(srpm.RPMParseException):
            srpm.parse_rpm_name('foo.rpm')
        with self.assertRaises(srpm.RPMParseException):
            srpm.parse_rpm_name('foo-1.3.x86.rpm')
