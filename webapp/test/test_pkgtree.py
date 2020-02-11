"""Unit tests for pkgtree module."""
# pylint: disable=unused-argument

from test import schemas
from test import tools
from test.conftest import TestBase

import decimal  # Necessary for loading successfully test data from .yml file

import pytest

from pkgtree import PkgtreeAPI

PKG = 'kernel-rt'
PKGS = ['kernel', 'kernel-rt']
PKG_JSON = {"package_name_list": [PKG]}
PKGS_JSON = {"package_name_list": PKGS}
PKG_JSON_EMPTY_LIST = {"package_name_list": [""]}
PKG_JSON_NON_EXIST = {"package_name_list": ["non-exist"]}


EMPTY_RESPONSE = {"package_name_list": {"": []}}
NON_EXIST_RESPONSE = {"package_name_list": {"non-exist": []}}


# TODO add tests for sorting
# TODO add tests for modularity


class TestPkgtreeAPI(TestBase):
    """Test pkgtree api class."""

    pkg_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup PkgtreeAPI object."""
        self.pkg_api = PkgtreeAPI(self.cache)

    def test_schema(self):
        """Test pkgtree api response schema of valid input."""
        response = self.pkg_api.process_list(1, PKG_JSON)
        schemas.pkgtree_top_schema.validate(response)
        schemas.pkgtree_list_schema.validate(response["package_name_list"][PKG])
        assert len(response["package_name_list"].keys()) == 1  # One package name is expected
        assert len(response["package_name_list"][PKG]) >= 1  # At least one NEVRA for a package name is expected

    def test_schema_multiple_pkgnames(self):
        """Test pkgtree api response schema of valid input with multiple package names."""
        response = self.pkg_api.process_list(1, PKGS_JSON)
        schemas.pkgtree_top_schema.validate(response)
        assert len(response["package_name_list"].keys()) == 2  # Two package names are expected
        for pkg in PKGS:
            schemas.pkgtree_list_schema.validate(response["package_name_list"][pkg])
            assert len(response["package_name_list"][pkg]) >= 1  # At least one NEVRA for a package name is expected

    @pytest.mark.xfail
    def test_schema_rhel8_modularity(self):
        """Test pkgtree api response with rhel8 modularity respositories."""
        # For rhel8 modularity the only difference is that the rhel-8 nevras contain repositories
        # with items 'module_name' and 'module_stream'.
        response = self.pkg_api.process_list(1, PKG_JSON)
        # Find rhel-8 nevra
        rhel8_repos = None
        # TODO Add support for modules and streams to pkgtree and cache.yml test data
        for name in response['package_name_list'][PKG]:
            if name['nevra'].endswith('.el8.x86_64'):
                rhel8_repos = name['repositories']
        assert rhel8_repos is not None
        # Check its repository items
        for repo in rhel8_repos:
            assert 'module_name' in repo
            assert 'module_stream' in repo

    #@pytest.mark.xfail
    def test_pkgname_one_item(self):  # pylint: disable=R0201
        """Test pkgtree api with one package name."""
        # TODO - Is it acutally useful or possible to have a test like this?
        response = self.pkg_api.process_list(1, PKG_JSON)
        import pprint
        pprint.pprint(response)
        assert False

    @pytest.mark.xfail
    def test_pkgname_multiple_items(self):  # pylint: disable=R0201
        """Test pkgtree api with several package names."""
        # TODO - Is it acutally useful or possible to have a test like this?
        assert False

    def test_pkgname_empty_list(self):
        """Test pkgtree api with empty package_name_list."""
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_pkg(self):
        """Test pkgtree api with non existing package name."""
        response = self.pkg_api.process_list(1, PKG_JSON_NON_EXIST)
        assert tools.match(NON_EXIST_RESPONSE, response) is True

    def test_last_change(self):
        """Test 'last_change' attribute in pkgtree api response."""
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert 'last_change' in response
        response = self.pkg_api.process_list(1, PKG_JSON_NON_EXIST)
        assert 'last_change' in response
        response = self.pkg_api.process_list(1, PKG_JSON)
        assert 'last_change' in response
        response = self.pkg_api.process_list(1, PKGS_JSON)
        assert 'last_change' in response

    def test_sorting_nevras(self):
        """Test sorting of NEVRAs in pkgtree api response."""
        response = self.pkg_api.process_list(1, PKG_JSON)
        nevras = [val['nevra'] for val in response['package_name_list'][PKG]]
        expected = ['kernel-rt-2.6.33.9-rt31.66.el6rt.x86_64',
                    'kernel-rt-4.18.0-80.rt9.138.el8.x86_64']
        assert nevras == expected

    def test_sorting_erratas(self):
        """Test sorting of erratas in pkgtree api response."""
        # Errata
        response = self.pkg_api.process_list(1, PKG_JSON)
        erratas = response['package_name_list'][PKG][-1]['errata']
        assert erratas[0]['name'] == 'RHSA-2019:1174'
        assert erratas[1]['name'] == 'RHSA-2019:1175'
        # CVE
        assert erratas[0]['cve_list'] == ['CVE-2018-12126', 'CVE-2018-12127', 'CVE-2018-12130', 'CVE-2019-11091']
        assert erratas[1]['cve_list'] == ['CVE-2018-10126']

    def test_sorting_repositories(self):
        """Test sorting of repositories in pkgtree api response."""
        response = self.pkg_api.process_list(1, PKG_JSON)
        repos = [val['label'] for val in response['package_name_list'][PKG][-1]['repositories']]
        expected = ['rhel-8-for-x86_64-nfv-rpms', 'rhel-8-for-x86_64-nfv-rpms',
                    'rhel-8-for-x86_64-rt-rpms', 'rhel-8-for-x86_64-rt-rpms']
        assert repos == expected
