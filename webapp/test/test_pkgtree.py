"""Unit tests for pkgtree module."""
# pylint: disable=unused-argument

from test import schemas
from test import tools
from test.conftest import TestBase

import pytest

from pkgtree import PkgtreeAPI

PKG_JSON_EMPTY_LIST = {"package_name_list": [""]}
PKG_JSON_NON_EXIST = {"package_name_list": ["non-exist"]}

EMPTY_RESPONSE = {"package_name_list": {"": {}}}
NON_EXIST_RESPONSE = {"package_name_list": {"non-exist": {}}}


class TestPackagesAPI(TestBase):
    """Test pkgtree api class."""

    pkg_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup PkgtreeAPI object."""
        self.pkg_api = PackagesAPI(self.cache)

    @pytest.mark.xfail
    def test_schema(self):
        # TODO
        assert False

    @pytest.mark.xfail
    def test_schema_rhel8_modularity(self):
        # TODO
        assert False

    @pytest.mark.xfail
    def test_schema_multiple_pkgnames(self):
        # TODO
        assert False

    @pytest.mark.xfail
    def test_pkgname_one_item(self):
        # TODO
        assert False

    @pytest.mark.xfail
    def test_pkgname_multiple_items(self):
        # TODO
        assert False

    def test_pkgname_empty_list(self):
        """Test pkgtree api with empty package_name_list."""
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_pkg(self):
        """Test pkgtree api with non existing package name."""
        response = self.pkg_api.process_list(1, PKG_JSON_NON_EXIST)
        assert tools.match(NON_EXIST_RESPONSE, response) is True

    # TODO add tests for modularity - rhel-8 and its repos/modules
