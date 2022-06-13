"""
Unit test classes for modules module.
"""
# pylint: disable=no-self-use
from vmaas.reposcan.repodata.modules import ModuleMD


class TestModuleMD:
    """Test ModuleMD class."""

    def test_modules_loading(self):
        """Test modules.yaml loading and parsing."""
        mod = ModuleMD("test_data/repodata/modules.yaml")
        assert len(mod.modules) == 2
        keys = ("name", "stream", "version", "context", "arch", "artifacts", "default_stream", "profiles", "requires")
        assert len(keys) == len(mod.modules[0])
        assert all(key in mod.modules[0] for key in keys)
