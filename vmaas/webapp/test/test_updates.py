"""Unit tests for updates module."""
# pylint: disable=protected-access
# pylint: disable=unused-argument
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
from copy import deepcopy
import pytest

from vmaas.webapp.test import schemas
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.updates import UpdatesAPI

PKG = "my-pkg-1.1.0-1.el8.i686"
PKG_UNKNOWN = "my-pkg-1.1.1-1.el8.i686"
PKG_NONE_ARCH = "my-pkg-1.1.1-1.el8.(none)"
UPDATES_JSON = {
    "package_list": [PKG],
    "repository_list": ["rhel-7-server-rpms"],
    "releasever": "7Server",
    "basearch": "x86_64",
    "modules_list": [{'module_name': 'my-pkg', 'module_stream': '1'}]
}

UPDATES_JSON_3_OPT = UPDATES_JSON.copy()
UPDATES_JSON_3_OPT['third_party'] = True
UPDATES_JSON_3_OPT['optimistic_updates'] = True

UPDATES_JSON_UNKNOWN = UPDATES_JSON.copy()
UPDATES_JSON_UNKNOWN['package_list'] = [PKG_UNKNOWN]

UPDATES_JSON_UNKNOWN_OPT_UPD = UPDATES_JSON_UNKNOWN.copy()
UPDATES_JSON_UNKNOWN_OPT_UPD['optimistic_updates'] = True

UPDATES_JSON_UNKNOWN_OPT_UPD_2 = UPDATES_JSON_UNKNOWN_OPT_UPD.copy()
UPDATES_JSON_UNKNOWN_OPT_UPD_2["modules_list"] = [{'module_name': 'my-pkg', 'module_stream': '2'}]

UPDATES_JSON_PREFIX = UPDATES_JSON_3_OPT.copy()
UPDATES_JSON_PREFIX['repository_list'] = ["rhul-rhel-7-server-rpms"]

UPDATES_RESPONSE_2 = {
    'update_list': {PKG:
                    {'available_updates': [{'package': 'my-pkg-1.2.0-1.el8.i686',
                                            'erratum': 'RHBA-2015:0364',
                                            'repository': 'rhel-7-server-rpms',
                                            'basearch': 'x86_64', 'releasever': '7Server'}]}},
    'repository_list': ['rhel-7-server-rpms'],
    'releasever': '7Server',
    'basearch': 'x86_64',
    'modules_list': [{'module_name': 'my-pkg', 'module_stream': '1'}],
    'last_change': '2019-03-07T09:17:23.799995+00:00'}

UPDATES_RESPONSE_1 = deepcopy(UPDATES_RESPONSE_2)
UPDATES_RESPONSE_1['update_list'][PKG]['summary'] = 'Testing package summary...'
UPDATES_RESPONSE_1['update_list'][PKG]['description'] = 'Testing package (1.1.0) description...'

UPDATES_RESPONSE_2_UNKNOWN = deepcopy(UPDATES_RESPONSE_2)
UPDATES_RESPONSE_2_UNKNOWN['update_list'] = {PKG_UNKNOWN: UPDATES_RESPONSE_2['update_list'][PKG]}
UPDATES_RESPONSE_2_UNKNOWN_NONE = UPDATES_RESPONSE_2_UNKNOWN.copy()
UPDATES_RESPONSE_2_UNKNOWN_NONE['update_list'] = {PKG_UNKNOWN: {}}
UPDATES_RESPONSE_2_UNKNOWN_2 = deepcopy(UPDATES_RESPONSE_2_UNKNOWN)
UPDATES_RESPONSE_2_UNKNOWN_2['update_list'] = {PKG_UNKNOWN:
                                               {'available_updates': [{'basearch': 'x86_64',
                                                                       'erratum': 'RHBA-2015:0364',
                                                                       'package': 'my-pkg-2.0.0-1.el8.i686',
                                                                       'releasever': '7Server',
                                                                       'repository': 'rhel-7-server-rpms'},
                                                                      {'basearch': 'x86_64',
                                                                       'erratum': 'RHBA-2015:0364',
                                                                       'package': 'my-pkg-2.1.0-1.el8.i686',
                                                                       'releasever': '7Server',
                                                                       'repository': 'rhel-7-server-rpms'}]}}
UPDATES_RESPONSE_2_UNKNOWN_2["modules_list"] = [{'module_name': 'my-pkg', 'module_stream': '2'}]
UPDATES_JSON_REPO = {"package_list": [PKG], "repository_list": ["rhel-6-server-rpms"]}
UPDATES_JSON_RELEASE = {"package_list": [PKG], "releasever": "6Server"}
UPDATES_JSON_ARCH = {"package_list": [PKG], "basearch": "i386"}
UPDATES_JSON_NON_EXIST = {"package_list": ["non-exist"]}
UPDATES_JSON_EMPTY = {}
UPDATES_JSON_EMPTY_LIST = {"package_list": [""]}

EMPTY_RESPONSE = {"update_list": {"": {}}, "last_change": "2019-03-07T09:17:23.799995+00:00"}
NON_EXIST_RESPONSE = {"update_list": {"non-exist": {}}, "last_change": "2019-03-07T09:17:23.799995+00:00"}


class TestUpdatesAPI(TestBase):
    """Test updates api class."""

    updates_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup UpdatesAPI object."""
        self.updates_api = UpdatesAPI(self.cache)

    def test_process_input_pkg(self):
        """Test filtering out unknown (or without updates) package names."""
        pkgs, update_list = self.updates_api.process_input_packages(UPDATES_JSON)
        assert pkgs == {'my-pkg-1.1.0-1.el8.i686': {'parsed_nevra': ('my-pkg', '0', '1.1.0', '1.el8', 'i686')}}
        assert update_list == {'my-pkg-1.1.0-1.el8.i686': {}}

    def test_process_input_non_exist(self):
        """Test filtering out unknown non existing package."""
        pkgs, update_list = self.updates_api.process_input_packages(UPDATES_JSON_NON_EXIST)
        assert not pkgs
        assert update_list == {'non-exist': {}}

    def test_schema_v1(self):
        """Test schema of updates api v1."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(1, UPDATES_JSON_3_OPT.copy())
        assert schemas.updates_top_all_schema.validate(updates)
        assert schemas.updates_package_schema.validate(updates["update_list"][PKG])

    def test_schema_v2(self):
        """Test schema of updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_3_OPT.copy())
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
        updates = self.updates_api.process_list(1, UPDATES_JSON_3_OPT.copy())
        assert updates == UPDATES_RESPONSE_1

    def test_process_list_v2(self):
        """Test looking for package updates api v2."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_3_OPT.copy())
        assert updates == UPDATES_RESPONSE_2

    def test_process_list_v3(self):
        """Test looking for package updates api v3."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(3, UPDATES_JSON_3_OPT.copy())
        assert updates == UPDATES_RESPONSE_2

    def test_process_list_prefix_v3(self):
        """Test looking for package updates api v3 with prefixed repo names."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(3, UPDATES_JSON_PREFIX.copy())
        assert updates == UPDATES_RESPONSE_2

    @pytest.mark.parametrize("repository_list", [None, [], ["anything"]])
    def test_process_list_with_repo_paths_v3(self, repository_list):
        """Test looking for package updates api v3 with repository paths."""
        pkg = "rhui-pkg-1.1.0-1.el7.x86_64"
        data = {
            "package_list": [pkg],
            "repository_list": repository_list,
            "repository_paths": ["/content/dist/rhel/rhui/server/7/7Server/x86_64/os/"],
            "releasever": "7Server",
            "basearch": "x86_64",
        }
        updates = self.updates_api.process_list(3, data)
        assert "update_list" in updates
        assert len(updates['update_list']) == 1
        assert pkg in updates["update_list"]
        assert "available_updates" in updates["update_list"][pkg]
        assert len(updates['update_list'][pkg]['available_updates']) == 1
        assert updates['update_list'][pkg]['available_updates'][0]["erratum"] == "RHBA-2015:0777"

    def test_process_none_arch(self):
        """Test pkg with arch (none)."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates_json_none = UPDATES_JSON_3_OPT.copy()
        updates_json_none['package_list'] = [PKG, PKG_NONE_ARCH]
        updates = self.updates_api.process_list(3, updates_json_none)
        assert len(updates['update_list']) == 2
        assert len(updates['update_list'][PKG]['available_updates']) == 1
        assert len(updates['update_list'][PKG_NONE_ARCH]['available_updates']) == 0

    def test_optimistic_updates_1(self):
        """Test looking for unknown EVRA updates (module_stream: 1)."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_UNKNOWN_OPT_UPD.copy())
        assert updates == UPDATES_RESPONSE_2_UNKNOWN

    def test_optimistic_updates_2(self):
        """Test looking for unknown EVRA updates (module_stream: 2)."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.updates_api.process_list(2, UPDATES_JSON_UNKNOWN_OPT_UPD_2.copy())
        assert updates == UPDATES_RESPONSE_2_UNKNOWN_2

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
        assert not repo_ids

    def test_get_repository_list_4(self):
        """Test with 'releasever' only request."""
        repositories_list, repo_ids = self.updates_api._get_repository_list(UPDATES_JSON_RELEASE)
        assert repositories_list is None
        assert list(repo_ids) == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_get_repository_list_5(self):
        """Test with 'basearch' only request."""
        repositories_list, repo_ids = self.updates_api._get_repository_list(UPDATES_JSON_ARCH)
        assert repositories_list is None
        assert list(repo_ids) == [1, 2, 3, 4, 5, 6, 7, 8]

    def test_get_repository_paths(self):
        """Test get repository paths and their corresponding ids."""
        data = {'repository_paths': ['/content/dist/rhel/rhui/server/7/7Server/x86_64/os/']}
        repository_paths, repo_ids = self.updates_api._get_repository_paths(data, [999])
        assert repository_paths == ['/content/dist/rhel/rhui/server/7/7Server/x86_64/os/']
        assert 7 in repo_ids, "repository not found by path"
        assert 999 in repo_ids, "previously found repository not returned back"

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
        assert not repo_ids

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
