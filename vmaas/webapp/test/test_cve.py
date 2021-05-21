"""Unit test for CveAPI module."""
# pylint: disable=unused-argument

import pytest
import pytz

from vmaas.webapp.test import schemas, tools
from vmaas.webapp.test.conftest import TestBase
from vmaas.common.webapp_utils import parse_datetime
from vmaas.webapp.cache import CVE_MODIFIED_DATE, CVE_PUBLISHED_DATE
from vmaas.webapp.cve import CveAPI


CVE_NAME = "CVE-2014-1545"
DATE_IN_FUTURE = "2099-01-01T00:00:00+00:00"
DATE_SINCE = "2018-04-06T01:23:45+02:00"
CVE_JSON_EMPTY = {}
CVE_JSON_BAD = {"modified_since": "2018-04-05T01:23:45+02:00"}
CVE_JSON = {"cve_list": [CVE_NAME]}
CVE_JSON_MODIFIED = {"cve_list": [CVE_NAME], "modified_since": DATE_SINCE}
CVE_JSON_PUBLISHED = {"cve_list": [CVE_NAME], "published_since": DATE_SINCE}
CVE_JSON_EMPTY_CVE = {"cve_list": [""]}
CVE_JSON_NON_EXIST = {"cve_list": ["CVE-9999-9999"]}

EMPTY_RESPONSE = {"cve_list": {}, "page": 1, "page_size": 0, "pages": 0,
                  "last_change": "2019-03-07T09:17:23.799995+00:00"}
CORRECT_RESPONSE = {
    "cvss2_score": "5.100",
    "impact": "Moderate",
    "synopsis": CVE_NAME,
    "package_list": ["my-pkg-1.1.0-1.el8.i686"],
    "source_package_list": ["my-pkg-1.1.0-1.el8.src"],
    "errata_list": ["RHBA-2015:0364"],
}


class TestCveAPI(TestBase):
    """Test CveAPI class."""

    cve = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Set CveAPI object"""
        # WORKAROUND: tzinfo from date is lost after loading YAML
        cve_detail = self.cache.cve_detail[CVE_NAME]
        cve_detail_list = list(cve_detail)
        cve_detail_list[CVE_MODIFIED_DATE] = cve_detail[CVE_MODIFIED_DATE].replace(tzinfo=pytz.utc)
        cve_detail_list[CVE_PUBLISHED_DATE] = cve_detail[CVE_PUBLISHED_DATE].replace(tzinfo=pytz.utc)
        self.cache.cve_detail[CVE_NAME] = cve_detail_list

        # make cve_detail without CVE_MODIFIED_DATE and CVE_PUBLISHED_DATE
        cve_detail2 = self.cache.cve_detail[CVE_NAME]
        cve_detail_list2 = list(cve_detail2)
        cve_detail_list2[CVE_MODIFIED_DATE] = None
        cve_detail_list2[CVE_PUBLISHED_DATE] = None
        self.cache.cve_detail["CVE-W/O-MODIFIED"] = cve_detail_list2
        self.cache.cve_detail["CVE-W/O-PUBLISHED"] = cve_detail_list2

        # Initialize CveAPI
        self.cve = CveAPI(self.cache)

    def test_regex(self):
        """Test finding CVEs by correct regex."""
        assert self.cve.try_expand_by_regex([CVE_NAME]) == [CVE_NAME]
        assert self.cve.try_expand_by_regex(["CVE-2014-.*"]) == [CVE_NAME]

    def test_wrong_regex(self):
        """Test CVE API with wrong regex."""
        with pytest.raises(Exception) as context:
            _ = self.cve.try_expand_by_regex(["*"])
        assert "nothing to repeat" in str(context.value)

    def test_empty_cve_list(self):
        """Test CVE API with with empty 'cve_list' property."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON_EMPTY_CVE)
        assert response == EMPTY_RESPONSE

    def test_non_existing_cve(self):
        """Test CVE API response with non-existing CVE."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON_NON_EXIST)
        assert response == EMPTY_RESPONSE

    def test_cve_response(self):
        """Test if CVE API response is correct for correct JSON."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON)
        assert schemas.cves_schema.validate(response)
        assert CVE_NAME in response["cve_list"]
        assert tools.match(CORRECT_RESPONSE, response["cve_list"][CVE_NAME]) is True

    def test_modified_since(self):
        """Test CVE API with 'modified_since' property."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON_MODIFIED)
        modified_from_resp = parse_datetime(response['cve_list'][CVE_NAME]['modified_date'])
        modified_since = parse_datetime(DATE_SINCE)
        assert modified_from_resp >= modified_since

    def test_modified_in_future(self):
        """Test CVE API with 'modified_since' property in future."""
        cve = CVE_JSON_MODIFIED.copy()
        cve["modified_since"] = DATE_IN_FUTURE
        response = self.cve.process_list(api_version=1, data=cve)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_without_modified(self):
        """Test CVEs without modified date. In response {modified_date: None}."""
        cve = CVE_JSON_MODIFIED.copy()
        cve["cve_list"] = ["CVE-W/O-MODIFIED"]
        response = self.cve.process_list(api_version=1, data=cve)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_published_since(self):
        """Test CVE API with 'published_since' property."""
        cve = CVE_JSON_PUBLISHED.copy()
        # correct date since publish of dummy cve
        cve["published_since"] = "2013-01-01T00:00:00+02:00"
        response = self.cve.process_list(api_version=1, data=cve)
        assert response["cve_list"][CVE_NAME]["synopsis"] == CVE_NAME

    def test_published_in_future(self):
        """Test CVE API with 'published_since' property with date in future"""
        cve = CVE_JSON_PUBLISHED.copy()
        cve["published_since"] = DATE_IN_FUTURE
        response = self.cve.process_list(api_version=1, data=cve)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_without_published(self):
        """Test CVEs without published date. In response {public_date: None}."""
        cve = CVE_JSON_PUBLISHED.copy()
        cve["cve_list"] = ["CVE-W/O-PUBLISHED"]
        response = self.cve.process_list(api_version=1, data=cve)
        assert tools.match(EMPTY_RESPONSE, response) is True
