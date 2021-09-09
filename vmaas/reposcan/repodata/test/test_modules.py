"""
Unit test classes for modules module.
"""
import unittest
from vmaas.reposcan.repodata.modules import ModuleMD


class TestModuleMD(unittest.TestCase):
    """Test ModuleMD class."""

    def test_modules_loading(self):
        """Test modules.yaml loading and parsing."""
        mod = ModuleMD("test_data/repodata/modules.yaml")
        self.assertEqual(2, len(mod.modules))
        keys = ['name', 'stream', 'version', 'context',
                    'arch', 'artifacts', 'default_stream',
                    'profiles', 'requires']
        self.assertEqual(len(keys), len(mod.modules[0]))
        for key in keys:
            self.assertIn(key, mod.modules[0])
