"""
Unit test classes for primary module.
"""
# pylint: disable=no-self-use
from xml.etree.ElementTree import ParseError
import pytest
from vmaas.reposcan.repodata.primary import PrimaryMD


class TestPrimaryMD:
    """Test PrimaryMD class."""

    def _test_package(self, pkg):
        intended_fields = ("name", "epoch", "ver", "rel", "arch", "summary", "description", "srpm")
        actual_fields = pkg.keys()
        for field in intended_fields:
            assert field in actual_fields
        for field in actual_fields:
            assert field in intended_fields
            assert isinstance(pkg[field], str)

    def test_invalid_file(self):
        """Test case when file doesn't exist or is invalid."""
        with pytest.raises(FileNotFoundError):
            PrimaryMD("/file/does/not/exist")
        with pytest.raises(ParseError):
            PrimaryMD("/dev/null")

    def test_packages(self):
        """Test parsed package metadata fields and counts."""
        primary = PrimaryMD("test_data/repodata/primary.xml")
        pkg_count = primary.get_package_count()
        packages = primary.list_packages()
        # Package count read from field and number of actually parsed packages should be same
        assert len(packages) == pkg_count
        assert pkg_count == 12
        # Test fields of packages in list
        for pkg in packages:
            self._test_package(pkg)
