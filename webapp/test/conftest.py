"""Configuration of pytest."""
# pylint: disable=redefined-outer-name

from test.yaml_cache import YamlCache

import pytest


@pytest.fixture(scope="session")
def load_data_once():
    """Load test data only once for whole test case."""
    cache = YamlCache("test/data/cache.yml")
    return cache.load_yaml()


class TestBase:
    """TestBase class. Setup self.cache for tests."""

    cache = None

    @pytest.fixture
    def load_cache(self, load_data_once):
        """Assign loaded data to self.cache."""
        self.cache = load_data_once
