"""Unit tests for dbchange module."""

import pytest

from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.dbchange import DBChange


class TestDBChange(TestBase):
    """Test dbchange api class."""

    db_api = None

    # pylint: disable=unused-argument
    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup DBChange object."""
        self.db_api = DBChange(self.cache)

    def test_keys(self):
        """Assert that dbchange return expected keys."""
        keys = ("cve_changes", "errata_changes", "exported", "last_change", "repository_changes")
        dbchange = self.db_api.process()
        for key in keys:
            assert key in dbchange
