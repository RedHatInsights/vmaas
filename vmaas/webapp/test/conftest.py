"""Configuration of pytest."""
# pylint: disable=redefined-outer-name,import-error,wrong-import-order
import pytest
import os
import redis

from vmaas.webapp.test import yaml_cache

# pylint: disable=invalid-name
pytest_plugins = 'aiohttp.pytest_plugin'


@pytest.fixture(scope="session")
def load_data_once():
    """Load test data only once for whole test case."""
    return yaml_cache.load_test_cache()


@pytest.fixture(scope="session")
def redis_conn():
    """Init testing Redis connection"""
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "FILL"),
        port=int(os.getenv("REDIS_PORT", "FILL")),
        password=os.getenv("REDIS_PASSWORD", "FILL")
    )
    reset_redis_data(r)
    yield r


def reset_redis_data(redis_conn: redis.Redis):
    """Reset testing data in Redis"""
    redis_conn.flushall()
    redis_conn.sadd("u:pA", 1, 2, 3, 4, 5, 6)
    redis_conn.sadd("a:x86", 2, 4, 6)
    redis_conn.sadd("a:i686", 1, 3, 5)
    redis_conn.set(1, "pA-1-1.el7.i686 ER7-1")
    redis_conn.set(2, "pA-1-1.el7.x86 ER7-1")
    redis_conn.set(3, "pA-1.1-1.el7.i686 ER7-2")
    redis_conn.set(4, "pA-1.1-1.el7.x86 ER7-2")
    redis_conn.set(5, "pA-2-1.el8.i686 ER8-1")
    redis_conn.set(6, "pA-2-1.el8.x86 ER8-1")
    redis_conn.sadd("r:rhel7", 1, 2, 3, 4)
    redis_conn.sadd("r:rhel8", 5, 6)


class TestBase:
    """TestBase class. Setup self.cache for tests."""

    cache = None

    @pytest.fixture
    def load_cache(self, load_data_once):
        """Assign loaded data to self.cache."""
        self.cache = load_data_once
