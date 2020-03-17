"""Configuration of pytest."""
# pylint: disable=redefined-outer-name,import-error,wrong-import-order
import pytest
from pytest_elasticsearch.factories import elasticsearch_proc, elasticsearch

from test import yaml_cache

# pylint: disable=invalid-name
pytest_plugins = 'aiohttp.pytest_plugin'

es_proc = elasticsearch_proc()
init_es = elasticsearch("es_proc")

@pytest.fixture(scope="session")
def load_data_once():
    """Load test data only once for whole test case."""
    return yaml_cache.load_test_cache()


class TestBase:
    """TestBase class. Setup self.cache for tests."""

    cache = None
    es_conn = None

    @pytest.fixture
    def load_cache(self, load_data_once):
        """Assign loaded data to self.cache."""
        self.cache = load_data_once

    @pytest.fixture
    def load_es(self, init_es):
        """Initialize ES connection."""
        self.es_conn = init_es
