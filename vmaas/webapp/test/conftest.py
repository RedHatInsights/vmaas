"""Configuration of pytest."""
# pylint: disable=redefined-outer-name,import-error,wrong-import-order
import pytest

from vmaas.webapp.test import yaml_cache

# pylint: disable=invalid-name


@pytest.fixture(scope="session")
def load_data_once():
    """Load test data only once for whole test case."""
    return yaml_cache.load_test_cache()


class TestBase:
    """TestBase class. Setup self.cache for tests."""

    cache = None

    @pytest.fixture
    def load_cache(self, load_data_once):
        """Assign loaded data to self.cache."""
        self.cache = load_data_once
