"""
Unit tests for checksum verification.
"""
import os
import shutil
import tempfile
from pathlib import Path

import pytest

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.repodata.checksum import verify_file_checksum, ChecksumError
from vmaas.reposcan.repodata.repository import Repository
from vmaas.reposcan.repodata.repository_controller import CHECKSUM_VERIFICATION_FAILED
from vmaas.reposcan.repodata.repository_controller import RepositoryController
from vmaas.reposcan.repodata.repomd import RepoMD

FIXTURE_DIR = Path(__file__).resolve().parents[2] / "test_data/repodata/checksum_fixtures"
GOOD_ARCHIVE = FIXTURE_DIR / "repodata/primary.xml.gz"
BAD_ARCHIVE = FIXTURE_DIR / "repodata/primary_bad.xml.gz"


class TestChecksum:
    """Test checksum verification."""

    def test_valid_sha256_checksum(self):
        """Test whether a file with correct SHA256 checksum passes verification."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content\n")
            temp_path = temp_file.name

        # SHA256 of "test content\n"
        expected = "a1fff0ffefb9eace7230c24e50731f0a91c62f9cefdfe77121c2f607125dffae"

        try:
            verify_file_checksum(temp_path, expected, "sha256")
        finally:
            os.unlink(temp_path)

    def test_invalid_checksum(self):
        """Test whether a file with wrong checksum raises ChecksumError."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content\n")
            temp_path = temp_file.name

        wrong_checksum = "0000000000000000000000000000000000000000000000000000000000000000"

        try:
            with pytest.raises(ChecksumError):
                verify_file_checksum(temp_path, wrong_checksum, "sha256")
        finally:
            os.unlink(temp_path)

    def test_valid_sha512_checksum(self):
        """Test whether SHA512 checksum verification works."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content\n")
            temp_path = temp_file.name

        # SHA512 of "test content\n"
        expected = ("b22137a0e8969282b85e3f9375448307d14c5aabf41be66c4f6a0323bd03a3935972021e4c34aa30914e37b03c22594fe"
                    "180eea9790e9ff147016c9dfae39d5a")

        try:
            verify_file_checksum(temp_path, expected, "sha512")
        finally:
            os.unlink(temp_path)

    def test_valid_sha1_checksum(self):
        """Test whether SHA1 checksum verification works."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content\n")
            temp_path = temp_file.name

        # SHA1 of "test content\n"
        expected = "4fe2b8dd12cd9cd6a413ea960cd8c09c25f19527"

        try:
            verify_file_checksum(temp_path, expected, "sha1")
        finally:
            os.unlink(temp_path)

    def test_case_insensitive_checksum(self):
        """Test whether checksum comparison is case-insensitive."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content\n")
            temp_path = temp_file.name

        # SHA256 in uppercase
        expected_upper = "A1FFF0FFEFB9EACE7230C24E50731F0A91C62F9CEFDFE77121C2F607125DFFAE"
        # SHA256 in lowercase
        expected_lower = "a1fff0ffefb9eace7230c24e50731f0a91c62f9cefdfe77121c2f607125dffae"
        # SHA256 in mixed case
        expected_mixed = "A1fff0ffEFB9eAcE7230c24e50731F0a91c62F9cefDFe77121c2F607125dffAE"

        try:
            # All should pass
            verify_file_checksum(temp_path, expected_upper, "sha256")
            verify_file_checksum(temp_path, expected_lower, "sha256")
            verify_file_checksum(temp_path, expected_mixed, "sha256")
        finally:
            os.unlink(temp_path)

    def test_unsupported_checksum_type(self):
        """Test whether unsupported checksum type raises ValueError."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            temp_file.write("test content\n")
            temp_path = temp_file.name

        try:
            with pytest.raises(ValueError):
                verify_file_checksum(temp_path, "dummy", "md4_nonexistent")
        finally:
            os.unlink(temp_path)


@pytest.fixture(name="controller")
def controller_fixture():
    """Minimal RepositoryController for _verify_metadata_checksums tests."""
    instance = RepositoryController.__new__(RepositoryController)
    # We just need this instance because RepositoryController never sets it
    instance.logger = get_logger(__name__)
    return instance


def _repository_with_archive(archive_path: Path) -> Repository:
    """Simulate a downloaded primary.xml.gz sitting in a repo temp directory."""
    tmp_directory = tempfile.mkdtemp(prefix="repo-checksum-test-")
    repomd = RepoMD(str(FIXTURE_DIR / "repomd.xml"))
    location = repomd.get_metadata("primary")["location"]
    target_name = os.path.basename(location)

    repo = Repository("https://whatever.com/repo/", "test-cs", "x86_64", "7", "Default")
    repo.tmp_directory = tmp_directory
    repo.repomd = repomd
    repo.md_files["primary"] = location
    shutil.copy(archive_path, os.path.join(tmp_directory, target_name))
    return repo


# pylint: disable=protected-access
class TestRepositoryControllerChecksum:
    """Test _verify_metadata_checksums with checksum_fixtures/."""

    def test_matching_archive_passes(self, controller):
        """primary.xml.gz matching repomd checksum should pass."""
        repo = _repository_with_archive(GOOD_ARCHIVE)
        try:
            assert controller._verify_metadata_checksums([repo]) == {}
        finally:
            shutil.rmtree(repo.tmp_directory, ignore_errors=True)

    def test_bad_archive_fails(self, controller):
        """primary_bad.xml.gz should fail checksum verification."""
        repo = _repository_with_archive(BAD_ARCHIVE)
        try:
            local_path = os.path.join(repo.tmp_directory, os.path.basename(repo.md_files["primary"]))
            failed = controller._verify_metadata_checksums([repo])
            assert failed == {local_path: CHECKSUM_VERIFICATION_FAILED}
        finally:
            shutil.rmtree(repo.tmp_directory, ignore_errors=True)
