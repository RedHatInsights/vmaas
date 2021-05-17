"""Unit tests for packages module."""
# pylint: disable=unused-argument

import pytest

from vmaas.webapp.test import schemas
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.rpm_pkg_names import RPMPkgNamesAPI

CS_LABEL = "my-content-set"
# RPM = "kernel-rt"
RPM = "my-pkg"
NONE_EXIST = "none-exist"
RPM_NAMES_JSON = {"rpm_name_list": [RPM]}
RPM_SRPM_NAMES_JSON = {"rpm_name_list": [RPM]}
RPM_CS_JSON = {"rpm_name_list": [RPM], "content_set_list": [CS_LABEL]}
RPM_JSON_EMPTY_LIST = {"rpm_name_list": [""]}
RPM_CS_JSON_EMPTY_LIST = {"rpm_name_list": [""], "content_set_list": [""]}
RPM_JSON_NON_EXIST = {"rpm_name_list": [NONE_EXIST]}
RPM_CS_JSON_NON_EXIST = {"rpm_name_list": [NONE_EXIST], "content_set_list": [NONE_EXIST]}
RPM_CS_NONEXIST = {"rpm_name_list": [RPM], "content_set_list": [NONE_EXIST]}

LAST_CHANGE = "2019-03-07T09:17:23.799995"
EMPTY_RPM_RESPONSE = {}
NON_EXIST_RPM_RESPONSE = {"none-exist": []}
EXIST_RPM_RESPONSE_EMPTY_CS = {f"{RPM}": []}


class TestRPMPkgNamesAPI(TestBase):
    """Test PackageNamesAPI class."""

    package_names_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup PackageNamesAPI object."""
        self.package_names_api = RPMPkgNamesAPI(self.cache)

    def test_rpm_schema(self):
        """Test PackageNamesAPI response schema of valid rpm_name_list input."""
        response = self.package_names_api.process_list(1, RPM_CS_JSON)
        schemas.pkg_names_rpm_schema.validate(response)
        assert len(response['rpm_name_list'][RPM]) == 1

    def test_rpm_content_set(self):
        """Test PackageNamesAPI response schema of valid rpm_name_list input."""
        response = self.package_names_api.process_list(1, RPM_NAMES_JSON)
        schemas.pkg_names_rpm_schema.validate(response)
        assert len(response['rpm_name_list'][RPM]) == 2

    def test_empty_rpm_list(self):
        """Test PackageNamesAPI with empty rpm list."""
        rpm_resp = self.package_names_api.process_list(1, RPM_JSON_EMPTY_LIST)
        assert EMPTY_RPM_RESPONSE == rpm_resp['rpm_name_list']

    def test_non_existing_rpms(self):
        """Test PackageNamesAPI with non existing rpms."""
        rpm_resp = self.package_names_api.process_list(1, RPM_JSON_NON_EXIST)
        assert EMPTY_RPM_RESPONSE == rpm_resp['rpm_name_list']

    def test_noex_content_set_ex_srpm(self):
        """Test PackageNamesAPI with existing rpm and nonexisting content set."""
        rpm_resp = self.package_names_api.process_list(1, RPM_CS_NONEXIST)
        assert EXIST_RPM_RESPONSE_EMPTY_CS == rpm_resp["rpm_name_list"]

    def test_last_change_in_resp(self):
        """Test PackageNamesAPI response contains last_change."""
        response = self.package_names_api.process_list(1, RPM_CS_JSON)
        assert 'last_change' in response
