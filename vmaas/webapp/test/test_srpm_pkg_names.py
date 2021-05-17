"""Unit tests for packages module."""
# pylint: disable=unused-argument
import pytest

from vmaas.webapp.test import schemas
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.srpm_pkg_names import SRPMPkgNamesAPI


CS_LABEL = "my-content-set"
RPM = "kernel-rt"
SRPM = "my-pkg"
NONE_EXIST = "none-exist"
SRPM_NAMES_JSON = {"srpm_name_list": [SRPM]}
SRPM_CS_JSON = {"srpm_name_list": [SRPM], "content_set_list": [CS_LABEL]}
SRPM_JSON_EMPTY_LIST = {"srpm_name_list": [""]}
SRPM_CS_JSON_EMPTY_LIST = {"srpm_name_list": [""], "content_set_list": [""]}
SRPM_JSON_NON_EXIST = {"srpm_name_list": [NONE_EXIST]}
SRPM_CS_JSON_NON_EXIST = {"srpm_name_list": [NONE_EXIST], "content_set_list": [NONE_EXIST]}
SRPM_CS_NON_EXIST = {"srpm_name_list": [SRPM], "content_set_list": [NONE_EXIST]}

LAST_CHANGE = "2019-03-07T09:17:23.799995"
EMPTY_SRPM_RESPONSE = {}
NON_EXIST_SRPM_RESPONSE = {f"{SRPM}": {}}


class TestSRPMPkgNamesAPI(TestBase):
    """Test PackageNamesAPI class."""

    package_names_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup PackageNamesAPI object."""
        self.package_names_api = SRPMPkgNamesAPI(self.cache)

    def test_srpm_schema(self):
        """Test PackageNamesAPI response schema of valid srpm_name_list input."""
        response = self.package_names_api.process_list(1, SRPM_NAMES_JSON)
        schemas.pkg_names_srpm_schema.validate(response)
        assert len(response['srpm_name_list'][SRPM]) == 2
        assert len(response['srpm_name_list'][SRPM][CS_LABEL]) == 1

    def test_content_set_schema(self):
        """Test PackageNamesAPI response schema of valid srpm_name_list and content_set_list input."""
        response = self.package_names_api.process_list(1, SRPM_CS_JSON)
        schemas.pkg_names_srpm_schema.validate(response)
        assert len(response['srpm_name_list'][SRPM][CS_LABEL]) == 1
        assert len(response['srpm_name_list'][SRPM]) == 1

    def test_empty_srpm_list(self):
        """Test PackageNamesAPI with empty srpm list."""
        srpm_resp = self.package_names_api.process_list(1, SRPM_JSON_EMPTY_LIST)
        assert EMPTY_SRPM_RESPONSE == srpm_resp['srpm_name_list']

    def test_empty_srpm_cs_list(self):
        """Test PackageNamesAPI with empty srpm and content set list."""
        srpm_cs_resp = self.package_names_api.process_list(1, SRPM_CS_JSON_EMPTY_LIST)
        assert EMPTY_SRPM_RESPONSE == srpm_cs_resp['srpm_name_list']

    def test_non_existing_srpms(self):
        """Test PackageNamesAPI with non existing srpm."""
        srpm_resp = self.package_names_api.process_list(1, SRPM_JSON_NON_EXIST)
        assert EMPTY_SRPM_RESPONSE == srpm_resp['srpm_name_list']

    def test_non_existing_content_set(self):
        """Test PackageNamesAPI with non existing srpm and content set."""
        srpm_cs_resp = self.package_names_api.process_list(1, SRPM_CS_JSON_NON_EXIST)
        assert EMPTY_SRPM_RESPONSE == srpm_cs_resp['srpm_name_list']

    def test_noex_content_set_ex_srpm(self):
        """Test PackageNamesAPI with existing srpm and nonexisting content set."""
        srpm_resp = self.package_names_api.process_list(1, SRPM_CS_NON_EXIST)
        assert NON_EXIST_SRPM_RESPONSE == srpm_resp["srpm_name_list"]

    def test_last_change_in_resp(self):
        """Test PackageNamesAPI response contains last_change."""
        response = self.package_names_api.process_list(1, SRPM_CS_JSON)
        assert 'last_change' in response
