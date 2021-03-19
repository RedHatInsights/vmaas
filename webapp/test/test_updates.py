"""Unit tests for updates module."""
# pylint: disable=protected-access
# pylint: disable=unused-argument
from test import schemas
from test.conftest import TestBase

import pytest

from updates import UpdatesAPI

PKG = "my-pkg-1.1.0-1.el8.i686"
UPDATES_JSON = {
    "package_list": [PKG],
    "repository_list": ["rhel-7-server-rpms"],
    "releasever": "7Server",
    "basearch": "x86_64",
    "modules_list": [{'module_name': 'my-pkg', 'module_stream': '1'}]
}
UPDATES_RESPONSE_1 = {
    'update_list': {'my-pkg-1.1.0-1.el8.i686':
                        {'summary': 'Testing package summary...',
                         'description': 'Testing package (1.1.0) description...',
                         'available_updates': [{'package': 'my-pkg-1.2.0-1.el8.i686',
                                                'erratum': 'RHBA-2015:0364',
                                                'repository': 'rhel-7-server-rpms',
                                                'basearch': 'x86_64', 'releasever': '7Server'}]}
                    },
    'repository_list': ['rhel-7-server-rpms'], 'releasever': '7Server', 'basearch': 'x86_64',
    'modules_list': [{'module_name': 'my-pkg', 'module_stream': '1'}]}

UPDATES_RESPONSE_2 = {
    'update_list': {'my-pkg-1.1.0-1.el8.i686':
                        {'available_updates': [{'package': 'my-pkg-1.2.0-1.el8.i686',
                                                'erratum': 'RHBA-2015:0364',
                                                'repository': 'rhel-7-server-rpms',
                                                'basearch': 'x86_64', 'releasever': '7Server'}]}},
    'repository_list': ['rhel-7-server-rpms'],
    'releasever': '7Server',
    'basearch': 'x86_64',
    'modules_list': [{'module_name': 'my-pkg', 'module_stream': '1'}]}

UPDATES_JSON_REPO = {"package_list": [PKG], "repository_list": ["rhel-6-server-rpms"]}
UPDATES_JSON_RELEASE = {"package_list": [PKG], "releasever": "6Server"}
UPDATES_JSON_ARCH = {"package_list": [PKG], "basearch": "i386"}
UPDATES_JSON_NON_EXIST = {"package_list": ["non-exist"]}
UPDATES_JSON_EMPTY = {}
UPDATES_JSON_EMPTY_LIST = {"package_list": [""]}

EMPTY_RESPONSE = {"update_list": {"": {}}}
NON_EXIST_RESPONSE = {"update_list": {"non-exist": {}}}


class TestUpdatesAPI(TestBase):
    """Test updates api class."""

    updates_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup UpdatesAPI object."""
        self.updates_api = UpdatesAPI(self.cache)

    def test_process_input_pkg(self):
        """Test filtering out unknown (or without updates) package names."""
        pkgs, update_list = self.updates_api._process_input_packages(UPDATES_JSON)
        assert pkgs == {'my-pkg-1.1.0-1.el8.i686': {'parsed_nevra': ('my-pkg', '0', '1.1.0', '1.el8', 'i686')}}
        assert update_list == {'my-pkg-1.1.0-1.el8.i686': {}}

    def test_process_input_non_exist(self):
        """Test filtering out unknown non existing package."""
        pkgs, update_list = self.updates_api._process_input_packages(UPDATES_JSON_NON_EXIST)
        assert pkgs == {}
        assert update_list == {'non-exist': {}}

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
        assert updates == UPDATES_RESPONSE_1

    def test_process_list_v2(self):
        """Test looking for package updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON.copy())
        assert updates == UPDATES_RESPONSE_2

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

class TestInternalUpdatesAPI(TestBase):
    """Test internal methods of updates api class."""

    updates_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup UpdatesAPI object."""
        self.updates_api = UpdatesAPI(self.cache)

    def test_get_repository_list_1(self):
        """Test with complete request."""
        repositories_list, repo_ids = self.updates_api._get_repository_list(UPDATES_JSON)
        assert repositories_list == ['rhel-7-server-rpms']
        assert repo_ids == [1]

    def test_get_repository_list_3(self):
        """Test with 'repository_list' only request."""
        repositories_list, repo_ids = self.updates_api._get_repository_list(UPDATES_JSON_REPO)
        assert repositories_list == ['rhel-6-server-rpms']
        assert repo_ids == []

    def test_get_repository_list_4(self):
        """Test with 'releasever' only request."""
        repositories_list, repo_ids = self.updates_api._get_repository_list(UPDATES_JSON_RELEASE)
        assert repositories_list is None
        assert list(repo_ids) == [1, 2, 3, 4, 5, 6]

    def test_get_repository_list_5(self):
        """Test with 'basearch' only request."""
        repositories_list, repo_ids = self.updates_api._get_repository_list(UPDATES_JSON_ARCH)
        assert repositories_list is None
        assert list(repo_ids) == [1, 2, 3, 4, 5, 6]

    def test_get_releasever_1(self):
        """Test with complete request"""
        repo_ids_in = [1]
        releasever, repo_ids = self.updates_api._get_releasever(UPDATES_JSON, repo_ids_in)
        assert releasever == '7Server'
        assert repo_ids == [1]

    def test_get_releasever_2(self):
        """Test with 'releasever' only request."""
        repo_ids_in = [1, 2, 3, 4, 5]
        releasever, repo_ids = self.updates_api._get_releasever(UPDATES_JSON_RELEASE, repo_ids_in)
        assert releasever == '6Server'
        assert repo_ids == []

    def test_get_releasever_3(self):
        """Test with 'basearch' only request."""
        repo_ids_in = [1, 2, 3, 4, 5]
        releasever, repo_ids = self.updates_api._get_releasever(UPDATES_JSON_ARCH, repo_ids_in)
        assert releasever is None
        assert repo_ids == repo_ids_in

    def test_get_basearch_1(self):
        """Test with complete request."""
        repo_ids_in = [1]
        basearch, repo_ids = self.updates_api._get_basearch(UPDATES_JSON, repo_ids_in)
        assert basearch == 'x86_64'
        assert repo_ids == {1}

    def test_get_basearch_2(self):
        """Test with 'repository_list' only request."""
        repo_ids_in = []
        basearch, repo_ids = self.updates_api._get_basearch(UPDATES_JSON_REPO, repo_ids_in)
        assert basearch is None
        assert repo_ids == set()

    def test_get_basearch_3(self):
        """Test with 'releasever' only request."""
        repo_ids_in = []
        basearch, repo_ids = self.updates_api._get_basearch(UPDATES_JSON_RELEASE, repo_ids_in)
        assert basearch is None
        assert repo_ids == set()

    def test_get_basearch_4(self):
        """Test with 'basearch' only request."""
        repo_ids_in = [1, 2, 3, 4, 5]
        basearch, repo_ids = self.updates_api._get_basearch(UPDATES_JSON_ARCH, repo_ids_in)
        assert basearch == 'i386'
        assert repo_ids == set()
