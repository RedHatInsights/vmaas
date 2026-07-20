"""
Unit tests for input validation.
"""
import pytest
from vmaas.reposcan.repodata.metadata_validators import (
    validate_cve_id,
    validate_bugzilla_id,
    validate_architecture,
    validate_package_name,
    validate_version,
    validate_release,
    ValidationError,
)


class TestCVEValidation:
    """Test CVE ID validation."""

    def test_valid_cve(self):
        """Test valid CVE IDs."""
        assert validate_cve_id("CVE-2024-1234") == "CVE-2024-1234"
        assert validate_cve_id("CVE-2023-12345678") == "CVE-2023-12345678"
        assert validate_cve_id("  CVE-2024-1234  ") == "CVE-2024-1234"  # Strips whitespace

    def test_invalid_cve_format(self):
        """Test invalid CVE ID formats."""
        with pytest.raises(ValidationError, match="Invalid CVE ID format"):
            validate_cve_id("INVALID-2024-1234")

        with pytest.raises(ValidationError, match="Invalid CVE ID format"):
            validate_cve_id("CVE-2024")  # Missing ID number

        with pytest.raises(ValidationError, match="Invalid CVE ID format"):
            validate_cve_id("CVE-24-1234")  # Year too short

        with pytest.raises(ValidationError, match="Invalid CVE ID format"):
            validate_cve_id("")

        with pytest.raises(ValidationError, match="Invalid CVE ID format"):
            validate_cve_id(None)


class TestBugzillaValidation:
    """Test Bugzilla ID validation."""

    def test_valid_bugzilla_id(self):
        """Test valid Bugzilla ticket numbers."""
        assert validate_bugzilla_id("1493960") == "1493960"
        assert validate_bugzilla_id("999999") == "999999"
        assert validate_bugzilla_id("  12345  ") == "12345"
        assert validate_bugzilla_id(12345) == "12345"  # Casts non-str to str

    def test_invalid_bugzilla_format(self):
        """Test invalid Bugzilla ID formats."""
        with pytest.raises(ValidationError, match="Invalid Bugzilla ID format"):
            validate_bugzilla_id("CVE-2024-1234")

        with pytest.raises(ValidationError, match="Invalid Bugzilla ID format"):
            validate_bugzilla_id("not-a-number")

        with pytest.raises(ValidationError, match="Invalid Bugzilla ID format"):
            validate_bugzilla_id("")

        with pytest.raises(ValidationError, match="Invalid Bugzilla ID format"):
            validate_bugzilla_id(None)


class TestArchitectureValidation:
    """Test architecture validation."""

    def test_valid_architectures(self):
        """Test valid architectures."""
        assert validate_architecture("x86_64") == "x86_64"
        assert validate_architecture("aarch64") == "aarch64"
        assert validate_architecture("noarch") == "noarch"
        assert validate_architecture("  x86_64  ") == "x86_64"

    def test_invalid_architecture(self):
        """Test invalid/unknown architectures."""
        with pytest.raises(ValidationError, match="Unknown architecture"):
            validate_architecture("invalid_arch")

        with pytest.raises(ValidationError, match="Unknown architecture"):
            validate_architecture("ARM64")  # Case sensitive

        with pytest.raises(ValidationError, match="Unknown architecture"):
            validate_architecture("")


class TestPackageNameValidation:
    """Test package name validation."""

    def test_valid_package_names(self):
        """Test valid package names."""
        assert validate_package_name("kernel") == "kernel"
        assert validate_package_name("python3.11") == "python3.11"
        assert validate_package_name("gcc-c++") == "gcc-c++"
        assert validate_package_name("lib_test-1.0") == "lib_test-1.0"

    def test_invalid_package_names(self):
        """Test invalid package names."""
        with pytest.raises(ValidationError, match="Invalid package name format"):
            validate_package_name("package with spaces")

        with pytest.raises(ValidationError, match="Invalid package name format"):
            validate_package_name("package@special")

        with pytest.raises(ValidationError, match="Invalid package name format"):
            validate_package_name("")


class TestVersionValidation:
    """Test version validation."""

    def test_valid_versions(self):
        """Test valid version strings."""
        assert validate_version("1.0.0") == "1.0.0"
        assert validate_version("5.14.0") == "5.14.0"
        assert validate_version("2.0~rc1") == "2.0~rc1"  # Tilde for pre-releases
        assert validate_version("1.el8_5") == "1.el8_5"
        assert validate_version("1.22^20260313git904aa67") == "1.22^20260313git904aa67"
        assert validate_version("0^20260319.75a7967") == "0^20260319.75a7967"
        assert validate_version("1.0.0.101^git20260123.39e7bd0") == "1.0.0.101^git20260123.39e7bd0"

    def test_invalid_versions(self):
        """Test invalid version strings."""
        with pytest.raises(ValidationError, match="Invalid"):
            validate_version("version with spaces")

        with pytest.raises(ValidationError, match="Invalid"):
            validate_version("1.0@invalid")

        with pytest.raises(ValidationError, match="Invalid"):
            validate_version("")


class TestReleaseValidation:
    """Test release validation."""

    def test_valid_releases(self):
        """Test valid release strings."""
        assert validate_release("1.el8") == "1.el8"
        assert validate_release("2.fc27") == "2.fc27"
        assert validate_release("1.module+el8+2517+b1471f1c") == "1.module+el8+2517+b1471f1c"
        assert validate_release("1~bootstrap") == "1~bootstrap"

    def test_invalid_releases(self):
        """Test invalid release strings."""
        with pytest.raises(ValidationError, match="Invalid"):
            validate_release("1.22^20260313git904aa67")  # ^ is version-only

        with pytest.raises(ValidationError, match="Invalid"):
            validate_release("rel with spaces")

        with pytest.raises(ValidationError, match="Invalid"):
            validate_release("")
