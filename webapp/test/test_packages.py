"""
Unit tests for packages module.
"""
# pylint: disable=unused-argument

from test import schemas
from test import tools
from test.conftest import TestBase
import time

import pytest

from packages import PackagesAPI, PackagesSearchAPI
from common.documents.nevra import Nevra, PACKAGES_INDEX
import common.webapp_utils as utils
from cache import REPO_LABEL, PKG_SOURCE_PKG_ID

PKG = "my-pkg-1.1.0-1.el8.i686"
PKG_SRC = "my-pkg-1.1.0-1.el8.src"
PKG_JSON = {"package_list": [PKG]}
PKG_SRC_JSON = {"package_list": [PKG_SRC]}
PKG_JSON_EMPTY_LIST = {"package_list": [""]}
PKG_JSON_NON_EXIST = {"package_list": ["non-exist"]}

EMPTY_RESPONSE = {"package_list": {"": {}}}
NON_EXIST_RESPONSE = {"package_list": {"non-exist": {}}}

# pylint: disable=line-too-long
SEARCH_EMPTY = {"nevra_pattern": {}}
SEARCH_EMPTY_WRONG = {"nevra_pattern": {"wrong": "request"}}
SEARCH_CORRECT = {"nevra_pattern": {"name": "my-pkg", "epoch": "0", "version": "1.1.0", "release": "1.el8", "arch": "i686"}}
SEARCH_NONEXISTING = {"nevra_pattern": {"name": "nonexisting-pkg", "epoch": "0", "version": "1.0.0", "release": "0.el8", "arch": "x86_64"}}
SEARCH_REGEX = {"nevra_pattern": {"name": "my-.*", "epoch": ".*", "version": "1.1..*", "release": "1.el.", "arch": ".*"}}
SEARCH_REGEX_ALL = {"nevra_pattern": {"name": ".*", "epoch": ".*", "version": ".*", "release": ".*", "arch": ".*"}}

SEARCH_EMPTY_RESPONSE = {"nevra_list": {}}
SEARCH_CORRECT_RESPONSE = {"nevra_list": {PKG: {"repositories": ["rhel-7-server-rpms"], "source_pkg": "my-pkg-1.1.0-1.el8.i686"}}}
SEARCH_REGEX_ALL_RESPONSE = {'nevra_list': {'my-pkg-1.1.0-1.el8.i686': {'repositories': ['rhel-7-server-rpms'], 'source_pkg': 'my-pkg-1.1.0-1.el8.i686'},
                                            'my-pkg-1.1.0-1.el8.src': {'repositories': [], 'source_pkg': None},
                                            'my-pkg-1.2.0-1.el8.i686': {'repositories': ['rhel-7-server-rpms'], 'source_pkg': None},
                                            'my-pkg-2.0.0-1.el8.i686': {'repositories': ['rhel-7-server-rpms'], 'source_pkg': None},
                                            'my-pkg-2.1.0-1.el8.i686': {'repositories': ['rhel-7-server-rpms'], 'source_pkg': None}}}

SEARCH_REGEX_RESPONSE = {'nevra_list': {'my-pkg-1.1.0-1.el8.i686': {'repositories': ['rhel-7-server-rpms'], 'source_pkg': 'my-pkg-1.1.0-1.el8.i686'},
                                        'my-pkg-1.1.0-1.el8.src': {'repositories': [], 'source_pkg': None}}}


class TestPackagesAPI(TestBase):
    """ Test dbchange api class. """

    pkg_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """ Setup PackageAPI object. """
        self.pkg_api = PackagesAPI(self.cache)

    def test_schema(self):
        """ Test pkg api response schema of valid input. """
        response = self.pkg_api.process_list(1, PKG_JSON)
        schemas.pkgs_top_schema.validate(response)
        schemas.pkgs_list_schema.validate(response["package_list"][PKG])
        assert len(response["package_list"][PKG]["repositories"]) == 1  # package is expected to be in one repo

    def test_schema_src(self):
        """ Test pkg api response schema of valid input. """
        response = self.pkg_api.process_list(1, PKG_SRC_JSON)
        schemas.pkgs_top_schema.validate(response)
        schemas.pkgs_list_schema.validate(response["package_list"][PKG_SRC])
        assert response["package_list"][PKG_SRC]["package_list"] == [PKG]
        assert not response["package_list"][PKG_SRC]["repositories"]  # source package is assigned to no repo

    def test_empty_pkg_list(self):
        """ Test pkg api with empty package_list. """
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_pkg(self):
        """ Test pkg api with non existing package. """
        response = self.pkg_api.process_list(1, PKG_JSON_NON_EXIST)
        assert tools.match(NON_EXIST_RESPONSE, response) is True


class TestPackagesSearchAPI(TestBase):
    """Tests for the packages search API."""

    pkg_search_api = None

    @pytest.fixture(autouse=True)
    def init_tests(self, load_es, load_cache):
        """ Init es fixture and fill it with data from cache. """
        PACKAGES_INDEX.create(using=self.es_conn)
        for nevra, pkg_id in self.cache.nevra2pkgid.items():
            nevra_es = Nevra()

            evr = self.cache.id2evr[nevra[1]]

            nevra_es.name = self.cache.id2packagename[nevra[0]]
            nevra_es.epoch = evr[0]
            nevra_es.version = evr[1]
            nevra_es.release = evr[2]
            nevra_es.arch = self.cache.id2arch[nevra[2]]

            nevra_es.repo_label = []

            try:
                for repo_id in self.cache.pkgid2repoids[pkg_id]:
                    nevra_es.repo_label.append(self.cache.repo_detail[repo_id][REPO_LABEL])
            except KeyError:
                pass

            try:
                src_pkg_detail = self.cache.package_details[pkg_id]
                src_pkg_id = src_pkg_detail[PKG_SOURCE_PKG_ID]
                nevra_es.source_pkg = None if not src_pkg_id else utils.pkg_detail2nevra(self.cache, src_pkg_detail)
            except KeyError:
                nevra_es.source_pkg = None

            nevra_es.save(using=self.es_conn)

        time.sleep(1) # ES takes time to index it
        self.pkg_search_api = PackagesSearchAPI(self.es_conn)


    def test_empty_request(self):
        """ Test empty request. """
        response = self.pkg_search_api.process_list(1, SEARCH_EMPTY)
        assert response == SEARCH_EMPTY_RESPONSE

    def test_wrong_request(self):
        """ Test wrong request. """
        response = self.pkg_search_api.process_list(1, SEARCH_EMPTY_WRONG)
        assert response == SEARCH_EMPTY_RESPONSE

    def test_regex_single(self):
        """ Test with single regex, matching src and i686 package. """
        response = self.pkg_search_api.process_list(1, SEARCH_REGEX)
        assert response == SEARCH_REGEX_RESPONSE

    def test_regex_all(self):
        """ Test fetch all records by regex. """
        response = self.pkg_search_api.process_list(1, SEARCH_REGEX_ALL)
        assert response == SEARCH_REGEX_ALL_RESPONSE

    def test_nevra_exact(self):
        """ Test exact package. """
        response = self.pkg_search_api.process_list(1, SEARCH_CORRECT)
        assert response == SEARCH_CORRECT_RESPONSE
