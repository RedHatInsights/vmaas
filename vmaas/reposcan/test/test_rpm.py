"""
Unit test classes for srpm module.
"""
import pytest
from vmaas.common import rpm_utils


class TestSrpm:
    """Test srpm module functions"""

    def test_parse_1_srpm(self):
        """Test parsing valid srpm name."""
        name, epoch, ver, rel, arch = rpm_utils.parse_rpm_name("389-ds-base-1.3.7.8-1.fc27.src.rpm")
        assert epoch is None
        assert name == "389-ds-base"
        assert ver == "1.3.7.8"
        assert rel == "1.fc27"
        assert arch == "src"

    def test_parse_2_rpm(self):
        """Test parsing valid rpm name."""
        name, epoch, ver, rel, arch = rpm_utils.parse_rpm_name("Agda-2.5.2-9.fc27.x86_64.rpm")
        assert epoch is None
        assert name == "Agda"
        assert ver == "2.5.2"
        assert rel == "9.fc27"
        assert arch == "x86_64"

    def test_parse_3_epoch(self):
        """Test parsing valid rpm name with epoch preceeding package name."""
        name, epoch, ver, rel, arch = rpm_utils.parse_rpm_name("3:Agda-2.5.2-9.fc27.x86_64.rpm")
        assert epoch == "3"
        assert name == "Agda"
        assert ver == "2.5.2"
        assert rel == "9.fc27"
        assert arch == "x86_64"

    def test_parse_4_epoch(self):
        """Test parsing valid rpm name with epoch preceeding version."""
        name, epoch, ver, rel, arch = rpm_utils.parse_rpm_name("perl-DBD-Pg-2:3.7.4-2.module+el8+2517+b1471f1c.x86_64")
        assert epoch == "2"
        assert name == "perl-DBD-Pg"
        assert ver == "3.7.4"
        assert rel == "2.module+el8+2517+b1471f1c"
        assert arch == "x86_64"

    def test_parse_5_epoch(self):
        """Test parsing valid rpm name with no epoch and specify default epoch"""
        name, epoch, ver, rel, arch = rpm_utils.parse_rpm_name("389-ds-base-1.3.7.8-1.fc27.src.rpm", default_epoch="1")
        assert epoch == "1"
        assert name == "389-ds-base"
        assert ver == "1.3.7.8"
        assert rel == "1.fc27"
        assert arch == "src"

    def test_parse_6_invalid_rpmname(self):
        """Test parsing invalid rpm name."""
        with pytest.raises(rpm_utils.RPMParseException):
            rpm_utils.parse_rpm_name("foo", raise_exception=True)
        with pytest.raises(rpm_utils.RPMParseException):
            rpm_utils.parse_rpm_name("foo.rpm", raise_exception=True)
        with pytest.raises(rpm_utils.RPMParseException):
            rpm_utils.parse_rpm_name("foo-1.3.x86.rpm", raise_exception=True)
        with pytest.raises(rpm_utils.RPMParseException):
            rpm_utils.parse_rpm_name("2:389-ds-base-4:1.3.7.8-1.fc27.src.rpm", raise_exception=True)

    def test_parse_7_invalid_noraise(self):
        """Test parsing invalid rpm name."""
        for name in [
            "foo",
            "foo.rpm",
            "foo-1.3.x86.rpm",
            "2:389-ds-base-4:1.3.7.8-1.fc27.src.rpm",
        ]:
            name, epoch, ver, rel, arch = rpm_utils.parse_rpm_name(name)
            assert epoch is None
            assert name == ""
            assert ver == ""
            assert rel == ""
            assert arch == ""


def test_rpmver2array_1():
    """Test rpmver array building."""
    assert rpm_utils.rpmver2array("1.a") == [(1, ""), (0, "a"), (-2, "")]
    assert rpm_utils.rpmver2array("1.a~rc1") == [(1, ""), (0, "a"), (-2, "rc"), (1, ""), (-2, "")]
    assert rpm_utils.rpmver2array("1.a^") == [(1, ""), (0, "a"), (-1, ""), (-2, "")]
