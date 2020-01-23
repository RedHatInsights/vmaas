"""Unit tests for pkgtree module."""
# pylint: disable=unused-argument

from test import schemas
from test import tools
from test.conftest import TestBase

import pytest

from pkgtree import PkgtreeAPI

PKG = 'kernel'
PKGS = ['kernel', 'kernel-rt']
PKG_JSON = {"package_name_list": [PKG]}
PKGS_JSON = {"package_name_list": PKGS}
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

    def test_schema(self):
        """Test pkg api response schema of valid input."""
        response = self.pkg_api.process_list(1, PKG_JSON)
        schemas.pkgtree_top_schema.validate(response)
        schemas.pkgtree_list_schema.validate(response["package_name_list"][PKG])
        assert len(response["package_name_list"].keys()) == 1  # One package name is expected
        assert len(response["package_name_list"][PKG]) >= 1  # At least one NEVRA for a package name is expected

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
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_pkgname_empty_list(self):
        """Test pkgtree api with empty package_name_list."""
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_pkg(self):
        """Test pkgtree api with non existing package name."""
        response = self.pkg_api.process_list(1, PKG_JSON_NON_EXIST)
        assert tools.match(NON_EXIST_RESPONSE, response) is True

    # TODO add tests for modularity - rhel-8 and its repos/modules
