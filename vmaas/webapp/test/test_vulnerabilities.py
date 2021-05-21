"""Unit tests for vulnerabilities module."""
# pylint: disable=protected-access
# pylint: disable=unused-argument

import pytest

from vmaas.webapp.test import schemas
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.updates import UpdatesAPI
from vmaas.webapp.vulnerabilities import VulnerabilitiesAPI

PKG = "bash-0:4.2.46-20.el7_2.x86_64"
UPDATES_JSON = {
    "package_list": [PKG],
    "repository_list": ["rhel-7-server-rpms"],
    "releasever": "7Server",
    "basearch": "x86_64",
}
UPDATES_JSON_NON_EXIST = {"package_list": ["non-exist"]}
UPDATES_JSON_EMPTY = {}
UPDATES_JSON_EMPTY_LIST = {"package_list": [""]}

EMPTY_RESPONSE = {"cve_list": [], "unpatched_cve_list": [], "last_change": "2019-03-07T09:17:23.799995+00:00"}


class TestVulnerabilitiesAPI(TestBase):
    """Test vulnerabilities api class."""

    vulnerabilities_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup UpdatesAPI object."""
        self.vulnerabilities_api = VulnerabilitiesAPI(self.cache, UpdatesAPI(self.cache))

    def test_schema(self):
        """Test schema of vulnerabilities api."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.vulnerabilities_api.process_list(1, UPDATES_JSON.copy())
        assert schemas.vulnerabilities_schema.validate(updates)

    def test_process_list(self):
        """Test looking for vulnerabilities api."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.vulnerabilities_api.process_list(1, UPDATES_JSON.copy())
        assert updates

    def test_process_empty_pkg_list(self):
        """Test empty package_list vulnberabilities api."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.vulnerabilities_api.process_list(1, UPDATES_JSON_EMPTY_LIST.copy())
        assert updates == EMPTY_RESPONSE

    def test_process_non_exist(self):
        """Test non-existing package vulnerabilities api."""
        # NOTE: use copy of dict with json input, because process_list changes this dict
        updates = self.vulnerabilities_api.process_list(1, UPDATES_JSON_NON_EXIST.copy())
        assert updates == EMPTY_RESPONSE
