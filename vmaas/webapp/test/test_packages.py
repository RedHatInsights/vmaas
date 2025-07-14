"""Unit tests for packages module."""
# pylint: disable=unused-argument

import pytest

from vmaas.webapp.test import schemas, tools
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.packages import PackagesAPI

PKG = "my-pkg-1.1.0-1.el8.i686"
PKG_SRC = "my-pkg-1.1.0-1.el8.src"
PKG_JSON = {"package_list": [PKG]}
PKG_SRC_JSON = {"package_list": [PKG_SRC]}
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
        assert len(response["package_list"][PKG]["repositories"]) == 1  # package is expected to be in one repo

    def test_schema_src(self):
        """Test pkg api response schema of valid input."""
        response = self.pkg_api.process_list(1, PKG_SRC_JSON)
        schemas.pkgs_top_schema.validate(response)
        schemas.pkgs_list_schema.validate(response["package_list"][PKG_SRC])
        assert response["package_list"][PKG_SRC]["package_list"] == [PKG]
        assert not response["package_list"][PKG_SRC]["repositories"]  # source package is assigned to no repo

    def test_empty_pkg_list(self):
        """Test pkg api with empty package_list."""
        response = self.pkg_api.process_list(1, PKG_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_pkg(self):
        """Test pkg api with non existing package."""
        response = self.pkg_api.process_list(1, PKG_JSON_NON_EXIST)
        assert tools.match(NON_EXIST_RESPONSE, response) is True
