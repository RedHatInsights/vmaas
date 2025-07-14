"""Unit tests for pkgtree module."""
# pylint: disable=unused-argument

from copy import deepcopy
import pytest

from vmaas.webapp.test import schemas, tools
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.pkgtree import PkgtreeAPI

PKG = 'kernel-rt'
PKGS = ['kernel', 'kernel-rt']
PKG_JSON = {"package_name_list": [PKG], "return_summary": True, "return_description": True}
PKGS_JSON = {"package_name_list": PKGS, "return_summary": True, "return_description": True}

RESPONSE_PKG = {'last_change': '2019-03-07T09:17:23.799995+00:00', 'page': 1, 'page_size': 1, 'pages': 1,
                'package_name_list': {'kernel-rt': [{'errata': [{'issued': '2011-06-23T00:00:00+00:00',
                                                                 'updated': '2011-06-23T00:00:00+00:00',
                                                                 'name': 'RHEA-2011:0895'}],
                                                     'first_published': '2011-06-23T00:00:00+00:00',
                                                     'summary': 'Testing package summary...',
                                                     'description': 'Testing package description...',
                                                     'nevra': 'kernel-rt-2.6.33.9-rt31.66.el6rt.x86_64',
                                                     'repositories': [{'basearch': 'x86_64',
                                                                       'label': 'rhel-8-for-x86_64-rt-rpms',
                                                                       'name': 'Red Hat '
                                                                               'Enterprise '
                                                                               'Linux 8 for '
                                                                               'x86_64 - Real '
                                                                               'Time (RPMs)',
                                                                       'releasever': '8.1',
                                                                       'revision': '2020-01-03T05:24:17+00:00'}]},
                                                    {'errata': [{'cve_list': ['CVE-2018-10126'],
                                                                 'issued': '2019-06-14T18:22:02+00:00',
                                                                 'updated': '2019-05-14T18:22:02+00:00',
                                                                 'name': 'RHSA-2019:1175'}],
                                                     'first_published': '2019-06-14T18:22:02+00:00',
                                                     'summary': 'Testing package summary...',
                                                     'description': 'Testing package description...',
                                                     'nevra': 'kernel-rt-4.18.0-80.rt9.138.el8.x86_64',
                                                     'repositories': [{'basearch': 'x86_64',
                                                                       'label': 'rhel-8-for-x86_64-rt-rpms',
                                                                       'name': 'Red Hat '
                                                                               'Enterprise '
                                                                               'Linux 8 for '
                                                                               'x86_64 - Real '
                                                                               'Time (RPMs)',
                                                                       'releasever': '8.1',
                                                                       'revision': '2020-01-03T05:24:17+00:00'}]}]}}


RESPONSE_PKGS = {
    'last_change': '2019-03-07T09:17:23.799995+00:00', 'page': 1, 'page_size': 2, 'pages': 1,
    'package_name_list': {'kernel': [{'errata': [],
                                      'first_published': '',
                                      'summary': 'Testing package summary...',
                                      'description': 'Testing package description...',
                                      'nevra': 'kernel-4.18.0-80.el8.x86_64',
                                      'repositories': []}],
                          PKG: RESPONSE_PKG['package_name_list'][PKG]}
}


PKG_JSON_EMPTY_LIST = {"package_name_list": [""]}
PKG_JSON_NON_EXIST = {"package_name_list": ["non-exist"]}


EMPTY_RESPONSE = {"package_name_list": {"": []}}
NON_EXIST_RESPONSE = {"package_name_list": {"non-exist": []}}


class TestPkgtreeAPI(TestBase):
    """Test pkgtree api class."""

    pkg_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup PkgtreeAPI object."""
        self.pkg_api = PkgtreeAPI(self.cache)

    def test_wrong_regex(self):
        """Test wrong errata regex."""
        with pytest.raises(Exception) as context:
            self.pkg_api.try_expand_by_regex(3, ["*"])
        assert "nothing to repeat" in str(context.value)

    def test_regex(self):
        """Test correct errata regex."""
        assert self.pkg_api.try_expand_by_regex(3, [PKG]) == [PKG]
        assert self.pkg_api.try_expand_by_regex(3, PKGS) == PKGS
        assert self.pkg_api.try_expand_by_regex(3, ["kernel-r.*"]) == [PKG]

    def test_schema(self):
        """Test pkgtree api response schema of valid input."""
        response = self.pkg_api.process_list(3, PKG_JSON)
        schemas.pkgtree_top_schema.validate(response)
        schemas.pkgtree_list_schema.validate(response["package_name_list"][PKG])
        assert len(response["package_name_list"].keys()) == 1  # One package name is expected
        assert len(response["package_name_list"][PKG]) >= 1  # At least one NEVRA for a package name is expected

    def test_schema_multiple_pkgnames(self):
        """Test pkgtree api response schema of valid input with multiple package names."""
        response = self.pkg_api.process_list(3, PKGS_JSON)
        schemas.pkgtree_top_schema.validate(response)
        assert len(response["package_name_list"].keys()) == 2  # Two package names are expected
        for pkg in PKGS:
            schemas.pkgtree_list_schema.validate(response["package_name_list"][pkg])
            assert len(response["package_name_list"][pkg]) >= 1  # At least one NEVRA for a package name is expected

    # FIXME Add support for modules and streams to pkgtree and cache.yml test data.
    @pytest.mark.xfail
    def test_schema_rhel8_modularity(self):
        """Test pkgtree api response with rhel8 modularity respositories."""
        # For rhel8 modularity the only difference is that the rhel-8 nevras contain repositories
        # with items 'module_name' and 'module_stream'.
        response = self.pkg_api.process_list(1, PKG_JSON)
        # Find rhel-8 nevra
        rhel8_repos = None
        for name in response['package_name_list'][PKG]:
            if name['nevra'].endswith('.el8.x86_64'):
                rhel8_repos = name['repositories']
        assert rhel8_repos is not None
        # Check its repository items
        for repo in rhel8_repos:
            assert 'module_name' in repo
            assert 'module_stream' in repo

    def test_pkgname_one_item(self):
        """Test pkgtree api with one package name."""
        response = self.pkg_api.process_list(3, PKG_JSON)
        assert response == RESPONSE_PKG

    def test_pkgname_modified_since(self):
        """Test pkgtree api 'modified_since' param set."""
        req = PKGS_JSON.copy()
        req["modified_since"] = '2015-04-05T01:23:45+00:00'
        response = self.pkg_api.process_list(3, req)
        exp = deepcopy(RESPONSE_PKGS)
        exp["package_name_list"]["kernel-rt"].pop(0)
        exp["package_name_list"]["kernel"] = []
        assert response == exp

    def test_pkgname_multiple_items(self):
        """Test pkgtree api with several package names."""
        response = self.pkg_api.process_list(3, PKGS_JSON)
        assert response == RESPONSE_PKGS

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
        assert erratas[0]['name'] == 'RHSA-2019:1175'
        # CVE
        assert erratas[0]['cve_list'] == ['CVE-2018-10126']

    def test_sorting_repositories(self):
        """Test sorting of repositories in pkgtree api response."""
        response = self.pkg_api.process_list(1, PKG_JSON)
        repos = [val['label'] for val in response['package_name_list'][PKG][-1]['repositories']]
        expected = ['rhel-8-for-x86_64-rt-rpms']
        assert repos == expected

    def test_third_party_on(self):
        """Test pkgtree with 'third_party' = True."""
        req = PKGS_JSON.copy()
        req["third_party"] = True
        req["package_name_list"] = [".*"]
        response = self.pkg_api.process_list(3, req)
        assert len(response["package_name_list"]) == 5
        assert len(response["package_name_list"]["third-party-pkg"]) == 1  # one package (third-party) found

    def test_third_party_off(self):
        """Test pkgtree with 'third_party' = False."""
        req = PKGS_JSON.copy()
        req["package_name_list"] = [".*"]
        response = self.pkg_api.process_list(3, req)
        assert len(response["package_name_list"]) == 5
        assert not response["package_name_list"]["third-party-pkg"]  # third-party package was excluded
