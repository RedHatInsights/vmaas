"""
Unit test classes for modules module.
"""
import unittest
from repodata.modules import ModuleMD


class TestModuleMD(unittest.TestCase):
    """Test ModuleMD class."""

    def test_modules_loading(self):
        """Test modules.yaml loading and parsing."""
        m = ModuleMD("test_data/repodata/modules.yaml")
        self.assertEqual(2, len(m.modules))
        self.assertEqual(8, len(m.modules[0]))
