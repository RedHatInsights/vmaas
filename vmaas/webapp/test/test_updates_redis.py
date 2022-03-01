"""Unit tests for updates redis module."""
import pytest

from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.updates_redis import UpdatesRedisAPI


class TestUpdatesRedisAPI(TestBase):
    """Test updates redis api class."""

    updates_redis_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, redis_conn):
        """Setup UpdatesRedisAPI object."""
        self.updates_redis_api = UpdatesRedisAPI(redis_conn)

    def test_updates_redis_1(self):
        """Test updates with Redis."""
        req = {"package_list": ["pA-1-1.el7.i686", "unknown-1-1.el8.i686"]}
        updates = self.updates_redis_api.process_list(req)
        resp = {'update_list': {'pA-1-1.el7.i686': [['pA-1.1-1.el7.i686', 'ER7-2'],
                                                    ['pA-2-1.el8.i686', 'ER8-1']],
                                'unknown-1-1.el8.i686': []}}
        assert updates == resp

    def test_updates_redis_2_optimistic(self):
        """Test updates with Redis."""
        req = {"package_list": ["pA-0-1.el8.i686", "unknown-1-1.el8.i686"]}  # this package is not in redis
        updates = self.updates_redis_api.process_list(req)
        resp = {'update_list': {'pA-0-1.el8.i686': [['pA-1-1.el7.i686', 'ER7-1'],
                                                    ['pA-1.1-1.el7.i686', 'ER7-2'],
                                                    ['pA-2-1.el8.i686', 'ER8-1']],
                                'unknown-1-1.el8.i686': []}}
        assert updates == resp

    def test_updates_redis_3_repo(self):
        """Test updates with Redis."""
        req = {"package_list": ["pA-1-1.el7.i686", "unknown-1-1.el8.i686"],
               "repository_list": ["rhel7"]}
        updates = self.updates_redis_api.process_list(req)
        resp = {'update_list': {'pA-1-1.el7.i686': [['pA-1.1-1.el7.i686', 'ER7-2']],
                                'unknown-1-1.el8.i686': []}}
        assert updates == resp

    def test_updates_redis_4_repo(self):
        """Test updates with Redis."""
        req = {"package_list": ["pA-1-1.el7.x86", "unknown-1-1.el8.i686"],
               "repository_list": ["rhel7", "rhel8"]}
        updates = self.updates_redis_api.process_list(req)
        resp = {'update_list': {'pA-1-1.el7.x86': [['pA-1.1-1.el7.x86', 'ER7-2'],
                                                   ['pA-2-1.el8.x86', 'ER8-1']],
                                'unknown-1-1.el8.i686': []}}
        assert updates == resp
