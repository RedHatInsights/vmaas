"""
Unit test classes for repomd module.
"""
from datetime import datetime
from xml.etree.ElementTree import ParseError
import pytest
from vmaas.reposcan.repodata.repomd import RepoMD, RepoMDTypeNotFound


class TestRepoMD:
    """Test RepoMD class."""

    @pytest.fixture
    def repomd(self):
        """Setup repomd file with all sections."""
        return RepoMD("test_data/repodata/repomd.xml")

    @pytest.fixture
    def repomd_primary_only(self):
        """Setup repomd file with primary section only."""
        return RepoMD("test_data/repodata/repomd_primary_only.xml")

    def test_revision(self, repomd, repomd_primary_only):
        """Test getting revision timestamp."""
        assert isinstance(repomd.get_revision(), datetime)
        assert isinstance(repomd_primary_only.get_revision(), datetime)
        assert repomd.get_revision() == repomd_primary_only.get_revision()

    def _test_repomd(self, data):
        intended_fields = {"location", "checksum_type", "checksum"}
        optional_fields = {"open-size", "size"}
        actual_fields = set(data.keys())
        assert set(actual_fields) == intended_fields.union(optional_fields)

    def test_invalid_file(self):
        """Test case when file doesn't exist or is invalid."""
        with pytest.raises(FileNotFoundError):
            RepoMD("/file/does/not/exist")
        with pytest.raises(ParseError):
            RepoMD("/dev/null")

    def test_get_primary(self, repomd, repomd_primary_only):
        """Test getting primary metadata info."""
        primary1 = repomd.get_metadata("primary")
        self._test_repomd(primary1)

        primary2 = repomd_primary_only.get_metadata("primary")
        self._test_repomd(primary2)

    def test_get_updateinfo(self, repomd, repomd_primary_only):
        """Test getting updateinfo metadata info."""
        updateinfo1 = repomd.get_metadata("updateinfo")
        self._test_repomd(updateinfo1)

        # Should fail
        with pytest.raises(RepoMDTypeNotFound):
            repomd_primary_only.get_metadata("updateinfo")
