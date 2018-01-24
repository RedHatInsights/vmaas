import unittest
from xml.etree.ElementTree import ParseError
from repodata.updateinfo import UpdateInfoMD

KNOWN_UPDATE_TYPES = ["security", "bugfix", "enhancement", "newpackage"]


class TestUpdateInfoMD(unittest.TestCase):
    def setUp(self):
        """Setup example updateinfo file."""
        self.updateinfo = UpdateInfoMD("test_data/repodata/updateinfo.xml")

    def _test_reference(self, reference):
        intended_fields = ["href", "id", "type", "title"]
        actual_fields = reference.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)

    def _test_pkg_ref(self, pkg_ref):
        intended_fields = ["name", "epoch", "ver", "rel", "arch"]
        actual_fields = pkg_ref.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)

    def _test_update(self, update):
        intended_fields = ["from", "status", "type", "version", "id", "title", "issued", "rights", "release",
                           "summary", "description", "references", "pkglist", "updated", "severity", "solution"]
        actual_fields = update.keys()
        for field in intended_fields:
            self.assertTrue(field in actual_fields)
        for field in actual_fields:
            self.assertTrue(field in intended_fields)

        self.assertIsInstance(update["references"], list)
        self.assertIsInstance(update["pkglist"], list)

        for reference in update["references"]:
            self._test_reference(reference)

        for pkg_ref in update["pkglist"]:
            self._test_pkg_ref(pkg_ref)

        # Check known update types
        self.assertTrue(update["type"] in KNOWN_UPDATE_TYPES)

    def test_invalid_file(self):
        with self.assertRaises(FileNotFoundError):
            UpdateInfoMD("/file/does/not/exist")
        with self.assertRaises(ParseError):
            UpdateInfoMD("/dev/null")

    def test_updates(self):
        updates = self.updateinfo.list_updates()
        # Test fields of updates in list
        for update in updates:
            self._test_update(update)
