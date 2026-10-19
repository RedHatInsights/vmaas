"""
Unit test classes for updateinfo module.
"""
from xml.etree.ElementTree import ParseError
import pytest
from vmaas.reposcan.repodata.updateinfo import UpdateInfoMD
from vmaas.reposcan.repodata.metadata_validators import ValidationError, validate_field

KNOWN_UPDATE_TYPES = ("security", "bugfix", "enhancement", "newpackage")


class TestUpdateInfoMD:
    """Test UpdateInfoMD class."""

    @pytest.fixture
    def updateinfo(self):
        """Setup example updateinfo file."""
        return UpdateInfoMD("test_data/repodata/updateinfo.xml")

    def _test_reference(self, reference):
        intended_fields = {"href", "id", "type", "title"}
        actual_fields = reference.keys()
        assert intended_fields == set(actual_fields)

    def _test_pkg_ref(self, pkg_ref):
        intended_fields = {"name", "epoch", "ver", "rel", "arch"}
        actual_fields = pkg_ref.keys()
        assert intended_fields == set(actual_fields)

    def _test_update(self, update):
        intended_fields = [
            "from",
            "status",
            "type",
            "version",
            "id",
            "title",
            "issued",
            "rights",
            "release",
            "summary",
            "description",
            "references",
            "pkglist",
            "updated",
            "severity",
            "solution",
            "reboot",
        ]
        actual_fields = update.keys()
        assert set(intended_fields) == set(actual_fields)

        assert isinstance(update["references"], list)
        assert isinstance(update["pkglist"], list)

        for reference in update["references"]:
            self._test_reference(reference)

        for pkg_ref in update["pkglist"]:
            self._test_pkg_ref(pkg_ref)

        self._test_reboot(update)

        # Check known update types
        assert update["type"] in KNOWN_UPDATE_TYPES

    def _test_reboot(self, update: dict):
        """Check that advisories with <reboot_suggested> tag were parsed correctly"""
        assert isinstance(update["reboot"], bool)
        is_update = update["id"] in ["FEDORA-2017-63f9b40927", "FEDORA-2017-14fbbab6e0", "FEDORA-2017-82315d72d0"]
        assert is_update == update["reboot"], f"{update['id']} - reboot"

    def test_invalid_file(self):
        """Test case when file doesn't exist or is invalid."""
        with pytest.raises(FileNotFoundError):
            UpdateInfoMD("/file/does/not/exist")
        with pytest.raises(ParseError):
            UpdateInfoMD("/dev/null")

    def test_updates(self, updateinfo):
        """Test parsed updates metadata fields and counts."""
        updates = updateinfo.list_updates()
        # Test fields of updates in list
        for update in updates:
            self._test_update(update)

    def test_valid_updates_pass(self):
        """Test that valid errata are imported."""
        ui_inst = UpdateInfoMD("test_data/repodata/update_validation_errata_test.xml")
        updates = ui_inst.list_updates()
        imported_ids = {u["id"] for u in updates}
        assert "vmaas_test_x86_64_1" in imported_ids
        assert "vmaas_test_i386_1.1" in imported_ids

    def test_skip_invalid_errata(self, caplog):
        """Test that errata with invalid fields are skipped."""
        ui_inst = UpdateInfoMD("test_data/repodata/update_validation_errata_test.xml")
        updates = ui_inst.list_updates()
        imported_ids = {u["id"] for u in updates}
        # 4 errata total, 2 invalid (bad arch + bad CVE) should be skipped
        assert len(updates) == 2
        assert "vmaas_test_x86_64_2" not in imported_ids
        assert "vmaas_test_i386_2.1" not in imported_ids
        assert caplog.text.count("Validation failed") == 2

    def test_valid_bugzilla_ref(self):
        """Test that type='bugzilla' with numeric id is validated and imported."""
        ui_inst = UpdateInfoMD("test_data/repodata/update_validation_errata_test.xml")
        updates = ui_inst.list_updates()
        update = next(u for u in updates if u["id"] == "vmaas_test_i386_1.1")
        assert len(update["references"]) == 1
        assert update["references"][0]["id"] == "999999"
        assert update["references"][0]["type"] == "bugzilla"

    def test_invalid_raises(self):
        """Test that validate_field raises ValidationError for invalid input."""
        with pytest.raises(ValidationError):
            validate_field("INVALID_ARCH", 'arch')
        with pytest.raises(ValidationError):
            validate_field("CVE-INVALID", 'cve_id')
        with pytest.raises(ValidationError):
            validate_field("not-a-number", 'bugzilla_id')
        with pytest.raises(ValidationError):
            validate_field("package with spaces", 'name')
