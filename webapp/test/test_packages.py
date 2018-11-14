"""Unit tests for packages module."""
# pylint: disable=unused-argument

from test import schemas
from test import tools
from test.conftest import TestBase

import pytest

from packages import PackagesAPI

PKG = "bash-0:4.2.46-20.el7_2.x86_64"
PKG_JSON_EMPTY = {}
PKG_JSON = {"package_list": [PKG]}
PKG_JSON_EMPTY_LIST = {"package_list": [""]}
PKG_JSON_NON_EXIST = {"package_list": ["non-exist"]}

EMPTY_RESPONSE = {"package_list": {"": {}}}
NON_EXIST_RESPONSE = {"package_list": {"non-exist": {}}}


class TestPackagesAPI(TestBase):
    """Test dbchange api class."""

    pkg_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup PackageAPI object."""
        self.pkg_api = PackagesAPI(self.cache)

    def test_schema(self):
        """Test pkg api response schema of valid input."""
        response = self.pkg_api.process_list(1, PKG_JSON)
        schemas.pkgs_top_schema.validate(response)
        schemas.pkgs_list_schema.validate(response["package_list"][PKG])

    def test_empty_json(self):
        """Test pkg api with empty json."""
        with pytest.raises(Exception) as context:
            self.pkg_api.process_list(1, PKG_JSON_EMPTY)
        assert "'package_list' is a required property" in str(context)

    def test_empty_pkg_list(self):
        """Test pkg api with empty package_list."""
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_pkg(self):
        """Test pkg api with non existing package."""
        response = self.pkg_api.process_list(1, PKG_JSON_NON_EXIST)
        assert tools.match(NON_EXIST_RESPONSE, response) is True
