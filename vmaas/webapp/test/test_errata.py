"""Unit tests for errata module."""
# pylint: disable=unused-argument

import pytest
import pytz

from vmaas.webapp.test import schemas
from vmaas.webapp.test import tools
from vmaas.webapp.test.conftest import TestBase
from vmaas.common.webapp_utils import parse_datetime
from vmaas.webapp.cache import ERRATA_UPDATED, ERRATA_ISSUED
from vmaas.webapp.errata import ErrataAPI

ERRATA_NAME = "RHBA-2015:0364"
MODIFIED_IN_FUTURE = "2099-01-01T00:00:00+00:00"
DATE_SINCE = "2014-04-06T01:23:45+02:00"
ERRATA_JSON = {"errata_list": [ERRATA_NAME]}
ERRATA_JSON_ALL = {"errata_list": [".*"]}
ERRATA_JSON_MODIFIED = {"errata_list": [ERRATA_NAME], "modified_since": DATE_SINCE}
ERRATA_JSON_EMPTY_LIST = {"errata_list": [""]}
ERRATA_JSON_NON_EXIST = {"errata_list": ["RHSA-9999:9999"]}

EMPTY_RESPONSE = {"errata_list": {}, "page": 1, "page_size": 0, "pages": 0}
CORRECT_RESPONSE = {'cve_list': ['CVE-2014-1545'],
                    'package_list': ['my-pkg-1.1.0-1.el8.i686'],
                    'source_package_list': ['my-pkg-1.1.0-1.el8.src']}


class TestErrataAPI(TestBase):
    """TestErrataAPI class. Test ErrataAPI class."""

    errata_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup ErrataAPI object from self.cache"""
        # WORKAROUND: tzinfo from date is lost after loading YAML
        errata_detail = self.cache.errata_detail[ERRATA_NAME]
        errata_detail_list = list(errata_detail)
        errata_detail_list[ERRATA_UPDATED] = errata_detail[ERRATA_UPDATED].replace(tzinfo=pytz.utc)
        errata_detail_list[ERRATA_ISSUED] = errata_detail[ERRATA_ISSUED].replace(tzinfo=pytz.utc)
        self.cache.errata_detail[ERRATA_NAME] = errata_detail_list

        # make errata_detail without ERRATA_UPDATED
        errata_detail2 = self.cache.errata_detail[ERRATA_NAME]
        errata_detail_list2 = list(errata_detail2)
        errata_detail_list2[ERRATA_UPDATED] = None
        errata_detail_list2[ERRATA_ISSUED] = None
        self.cache.errata_detail["RHSA-W/O:MODIFIED"] = errata_detail_list2

        self.errata_api = ErrataAPI(self.cache)

    def test_wrong_regex(self):
        """Test wrong errata regex."""
        with pytest.raises(Exception) as context:
            self.errata_api.try_expand_by_regex(["*"])
        assert "nothing to repeat" in str(context.value)

    def test_regex(self):
        """Test correct errata regex."""
        assert self.errata_api.try_expand_by_regex([ERRATA_NAME]) == [ERRATA_NAME]
        assert self.errata_api.try_expand_by_regex(["RHBA-2015:03.*"]) == [ERRATA_NAME]

    def test_empty_errata_list(self):
        """Test errata API with empty 'errata_list'."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_errata(self):
        """Test errata API repsonse for non-existent errata."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_NON_EXIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_third_party(self):
        """Test filtering with third party enabled"""
        data = {**ERRATA_JSON_ALL, "third_party": True}
        response = self.errata_api.process_list(api_version="v3", data=data)
        assert len(response["errata_list"]) == 7

    def test_non_third_party(self):
        """Test filtering with third-party content disabled"""
        data = {**ERRATA_JSON_ALL}
        data.pop("third_party", None)
        response = self.errata_api.process_list(api_version="v3", data=data)
        assert len(response["errata_list"]) == 6

    def test_errata_response(self):
        """Test errata API response."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON)
        assert schemas.errata_schema.validate(response)
        assert ERRATA_NAME in response["errata_list"]
        assert tools.match(CORRECT_RESPONSE, response["errata_list"][ERRATA_NAME]) is True

    def test_page_size(self):
        """Test errata API page size"""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON)
        page_size = len(response['errata_list'])
        assert response['page_size'] == page_size

    def test_modified_since(self):
        """Test errata API with 'modified_since' property."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_MODIFIED)
        modified_from_resp = parse_datetime(response['errata_list'][ERRATA_NAME]['updated'])
        modified_since = parse_datetime(DATE_SINCE)
        assert modified_from_resp >= modified_since

    def test_modified_in_future(self):
        """Test CVE API with 'modified_since' property in future."""
        errata = ERRATA_JSON_MODIFIED.copy()
        errata["modified_since"] = MODIFIED_IN_FUTURE
        response = self.errata_api.process_list(api_version="v1", data=errata)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_without_modified(self):
        """Test errata without modified date. In response  {updated: None}."""
        errata = ERRATA_JSON_MODIFIED.copy()
        errata["errata_list"] = ["RHSA-W/O:MODIFIED"]
        response = self.errata_api.process_list(api_version="v1", data=errata)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_errata_releasever(self):
        """Test errata API response."""
        response = self.errata_api.process_list(api_version="v3", data=ERRATA_JSON)
        assert ERRATA_NAME in response["errata_list"]
        relvers = response["errata_list"][ERRATA_NAME]["release_versions"]
        assert len(relvers) == 1
        assert relvers[0] == '7Server'
