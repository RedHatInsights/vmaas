"""Unit test for CveAPI module."""
# pylint: disable=unused-argument

import datetime

from test import schemas, tools
from test.conftest import TestBase

import pytest
import pytz

from cve import CveAPI
from cache import CVE_MODIFIED_DATE, CVE_PUBLISHED_DATE

CVE_JSON_EMPTY = {}
CVE_JSON_BAD = {"modified_since": "2018-04-05T01:23:45+02:00"}
CVE_JSON = {"cve_list": ["CVE-2016-0634"], "modified_since": "2018-04-06T01:23:45+02:00"}
CVE_JSON_EMPTY_CVE = {"cve_list": [""]}
CVE_JSON_NON_EXIST = {"cve_list": ["CVE-9999-9999"]}

EMPTY_RESPONSE = {"cve_list": {}, "page": 1, "page_size": 5000, "pages": 0}
CORRECT_RESPONSE = {
    "cvss3_score": "4.9",
    "impact": "Moderate",
    # "redhat_url": "https://access.redhat.com/security/cve/cve-2016-0634",
    "synopsis": "CVE-2016-0634",
    "package_list": ["bash-4.2.46-28.el7.x86_64"],
    "errata_list": ["RHSA-2017:1931"],
}


class TestCveAPI(TestBase):
    """Test CveAPI class."""

    cve = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Set CveAPI object"""
        # WORKAROUND: tzinfo from date is lost after loading YAML
        cve_detail = self.cache.cve_detail["CVE-2016-0634"]
        cve_detail_list = list(cve_detail)
        cve_detail_list[CVE_MODIFIED_DATE] = cve_detail[CVE_MODIFIED_DATE].replace(tzinfo=pytz.utc)
        cve_detail_list[CVE_PUBLISHED_DATE] = cve_detail[CVE_PUBLISHED_DATE].replace(tzinfo=pytz.utc)
        self.cache.cve_detail["CVE-2016-0634"] = cve_detail_list

        # make cve_detail without CVE_MODIFIED_DATE
        cve_detail2 = self.cache.cve_detail["CVE-2016-0634"]
        cve_detail_list2 = list(cve_detail2)
        cve_detail_list2[CVE_MODIFIED_DATE] = None
        self.cache.cve_detail["CVE-W/O-MODIFIED"] = cve_detail_list2

        # Initialize CveAPI
        self.cve = CveAPI(self.cache)

    def test_regex(self):
        """Test finding CVEs by correct regex."""
        assert self.cve.find_cves_by_regex("CVE-2018-5750") == ["CVE-2018-5750"]
        assert "CVE-2018-5750" in self.cve.find_cves_by_regex("CVE-2018-5.*")
        assert len(self.cve.find_cves_by_regex("CVE-2018-5.*")) > 1

    def test_wrong_regex(self):
        """Test CVE API with wrong regex."""
        with pytest.raises(Exception) as context:
            self.cve.find_cves_by_regex("*")
        assert "nothing to repeat" in str(context)

    def test_missing_required(self):
        """Test CVE API without required property 'cve_list'."""
        with pytest.raises(Exception) as context:
            self.cve.process_list(api_version=1, data=CVE_JSON_BAD)
        assert "'cve_list' is a required property" in str(context)

    def test_empty_json(self):
        """Test CVE API with empty JSON."""
        with pytest.raises(Exception) as context:
            self.cve.process_list(api_version=1, data=CVE_JSON_EMPTY)
        assert "'cve_list' is a required property" in str(context)

    def test_empty_cve_list(self):
        """Test CVE API with with empty 'cve_list' property."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON_EMPTY_CVE)
        assert response == EMPTY_RESPONSE

    def test_non_existing_cve(self):
        """Test CVE API response with non-existing CVE."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON_NON_EXIST)
        assert response == EMPTY_RESPONSE

    def test_schema(self):
        """Test CVE API response schema."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON)
        assert schemas.cves_schema.validate(response)

    def test_cve_response(self):
        """Test if CVE API response is correct for correct JSON."""
        response = self.cve.process_list(api_version=1, data=CVE_JSON)
        cve, = response["cve_list"].items()
        assert cve[0] == CVE_JSON["cve_list"][0]
        assert tools.match(CORRECT_RESPONSE, cve[1]) is True

    @pytest.mark.skip("Blocked by https://github.com/RedHatInsights/vmaas/issues/419")
    def test_modified_since(self):
        """Test CVE API with 'modified_since' property."""
        cve = CVE_JSON.copy()
        cve["modified_since"] = str(datetime.datetime.now().replace(tzinfo=pytz.UTC))
        response = self.cve.process_list(api_version=1, data=cve)
        assert tools.match(EMPTY_RESPONSE, response) is True

        # without modified date
        cve["cve_list"] = ["CVE-W/O-MODIFIED"]
        response = self.cve.process_list(api_version=1, data=cve)
        assert tools.match(EMPTY_RESPONSE, response) is True
