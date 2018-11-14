"""Unit tests for updates module."""
# pylint: disable=protected-access
# pylint: disable=unused-argument

import os

from test import schemas
from test.conftest import TestBase

import pytest

from updates import HotCache
from updates import UpdatesAPI

PKG = "bash-0:4.2.46-20.el7_2.x86_64"
UPDATES_JSON = {
    "package_list": [PKG],
    "repository_list": ["rhel-7-server-rpms"],
    "releasever": "7Server",
    "basearch": "x86_64",
}
UPDATES_JSON_REPO = {"package_list": [PKG], "repository_list": ["rhel-6-server-rpms"]}
UPDATES_JSON_RELEASE = {"package_list": [PKG], "releasever": "6Server"}
UPDATES_JSON_ARCH = {"package_list": [PKG], "basearch": "i386"}
UPDATES_JSON_NON_EXIST = {"package_list": ["non-exist"]}
UPDATES_JSON_EMPTY = {}
UPDATES_JSON_EMPTY_LIST = {"package_list": [""]}

EMPTY_RESPONSE = {"update_list": {"": {}}}
NON_EXIST_RESPONSE = {"update_list": {"non-exist": {}}}


class TestHotCache(TestBase):
    """Test HotCache class."""

    hot_cache = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup HotCache object."""
        os.environ["HOTCACHE_PRUNING"] = "5"
        os.environ["HOTCACHE_LEVELS"] = "3"
        self.hot_cache = HotCache()

    # TODO: write unit tests for Hot Cache


class TestUpdatesAPI(TestBase):
    """Test updates api class."""

    updates_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup UpdatesAPI object."""
        self.updates_api = UpdatesAPI(self.cache)

    def test_process_repos(self):
        """Test repos processing."""
        response = {}
        repo_ids = self.updates_api._process_repositories(UPDATES_JSON, response)
        assert repo_ids == {1}

    def test_process_repos_repo(self):
        """Test repos processing - filter out repository_list."""
        response = {}
        repo_ids = self.updates_api._process_repositories(UPDATES_JSON_REPO, response)
        assert repo_ids == set()

    def test_process_repos_release(self):
        """Test repos processing - filter out releasever."""
        response = {}
        repo_ids = self.updates_api._process_repositories(UPDATES_JSON_RELEASE, response)
        assert repo_ids == set()

    def test_process_repos_arch(self):
        """Test repos processing - filter out basearch."""
        response = {}
        repo_ids = self.updates_api._process_repositories(UPDATES_JSON_ARCH, response)
        assert repo_ids == set()

    def test_process_input_pkg(self):
        """Test filtering out unknown (or without updates) package names."""
        response = {}
        response["update_list"] = {}
        response["update_list"][PKG] = {}
        pkgs = self.updates_api._process_input_packages(UPDATES_JSON, response)
        assert pkgs

    def test_process_input_non_exist(self):
        """Test filtering out unknown non existing package."""
        response = {}
        response["update_list"] = {}
        response["update_list"][PKG] = {}
        pkgs = self.updates_api._process_input_packages(UPDATES_JSON_NON_EXIST, response)
        assert pkgs == {}

    def test_schema_v1(self):
        """Test schema of updates api v1."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(1, UPDATES_JSON.copy())
        assert schemas.updates_top_all_schema.validate(updates)
        assert schemas.updates_package_schema.validate(updates["update_list"][PKG])

    def test_schema_v2(self):
        """Test schema of updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON.copy())
        assert schemas.updates_top_all_schema.validate(updates)
        assert schemas.updates_package_schema_v2.validate(updates["update_list"][PKG])

    def test_schema_repolist(self):
        """Test repolist schema of updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_REPO.copy())
        assert schemas.updates_top_repolist_schema.validate(updates)

    def test_schema_releasever(self):
        """Test releasever schema of updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_RELEASE.copy())
        assert schemas.updates_top_releasever_schema.validate(updates)

    def test_schema_basearch(self):
        """Test basearch schema of updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_ARCH.copy())
        assert schemas.updates_top_basearch_schema.validate(updates)

    def test_process_list_v1(self):
        """Test looking for package updates api v1."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(1, UPDATES_JSON.copy())
        assert updates

    def test_process_list_v2(self):
        """Test looking for package updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON.copy())
        assert updates

    def test_process_empty_pkg_list_v1(self):
        """Test empty package_list updates api v1."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(1, UPDATES_JSON_EMPTY_LIST.copy())
        assert updates == EMPTY_RESPONSE

    def test_process_empty_pkg_list_v2(self):
        """Test empty package_list updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_EMPTY_LIST.copy())
        assert updates == EMPTY_RESPONSE

    def test_process_non_exist_v1(self):
        """Test non-existing package updates api v1."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(1, UPDATES_JSON_NON_EXIST.copy())
        assert updates == NON_EXIST_RESPONSE

    def test_process_non_exist_v2(self):
        """Test non-existing package updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_NON_EXIST.copy())
        assert updates == NON_EXIST_RESPONSE

    def test_process_list_empty_json(self):
        """Test updates API with empty json."""
        with pytest.raises(Exception) as context:
            # NOTE: use copy of dict with json input, because process_list changes this dict
            self.updates_api.process_list(1, UPDATES_JSON_EMPTY.copy())
        assert "'package_list' is a required property" in str(context)
