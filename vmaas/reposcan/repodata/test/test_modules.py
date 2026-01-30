"""
Unit test classes for modules module.
"""
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
        assert mod.modules[1]["name"] == "subversion"
        assert mod.modules[1]["stream"] == "1.10"
        assert all(key in mod.modules[1]["requires"]["dummy"] for key in ["1.30", "5.32", "4"])
