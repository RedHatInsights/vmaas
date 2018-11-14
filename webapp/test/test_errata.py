"""Unit tests for errata module."""
# pylint: disable=unused-argument

import datetime

from test import schemas
from test import tools
from test.conftest import TestBase

import pytest
import pytz

from cache import ERRATA_UPDATED, ERRATA_ISSUED
from errata import ErrataAPI


ERRATA_JSON_EMPTY = {}
ERRATA_JSON_BAD = {"modified_since": "2018-04-05T01:23:45+02:00"}
ERRATA_JSON = {"errata_list": ["RHSA-2018:1055"], "modified_since": "2018-04-06T01:23:45+02:00"}
ERRATA_JSON_EMPTY_LIST = {"errata_list": [""]}
ERRATA_JSON_NON_EXIST = {"errata_list": ["RHSA-9999:9999"]}

EMPTY_RESPONSE = {"errata_list": {}, "page": 1, "page_size": 5000, "pages": 0}


class TestErrataAPI(TestBase):
    """TestErrataAPI class. Test ErrataAPI class."""

    errata_api = None

    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Setup ErrataAPI object from self.cache"""
        # WORKAROUND: tzinfo from date is lost after loading YAML
        errata_detail = self.cache.errata_detail["RHSA-2018:1055"]
        errata_detail_list = list(errata_detail)
        errata_detail_list[ERRATA_UPDATED] = errata_detail[ERRATA_UPDATED].replace(tzinfo=pytz.utc)
        errata_detail_list[ERRATA_ISSUED] = errata_detail[ERRATA_ISSUED].replace(tzinfo=pytz.utc)
        self.cache.errata_detail["RHSA-2018:1055"] = errata_detail_list

        # make errata_detail without ERRATA_UPDATED
        errata_detail2 = self.cache.errata_detail["RHSA-2018:1055"]
        errata_detail_list2 = list(errata_detail2)
        errata_detail_list2[ERRATA_UPDATED] = None
        self.cache.errata_detail["RHSA-W/O:MODIFIED"] = errata_detail_list2

        self.errata_api = ErrataAPI(self.cache)

    def test_wrong_regex(self):
        """Test wrong errata regex."""
        with pytest.raises(Exception) as context:
            self.errata_api.find_errata_by_regex("*")
        assert "nothing to repeat" in str(context)

    def test_regex(self):
        """Test correct errata regex."""
        assert self.errata_api.find_errata_by_regex("RHSA-2018:1055") == ["RHSA-2018:1055"]
        assert "RHSA-2018:1055" in self.errata_api.find_errata_by_regex("RHSA-2018:1.*")
        assert len(self.errata_api.find_errata_by_regex("RHSA-2018:1.*")) > 1

    def test_missing_required(self):
        """Test missing required property 'errata_list'."""
        with pytest.raises(Exception) as context:
            self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_BAD)
        assert "'errata_list' is a required property" in str(context)

    def test_empty_json(self):
        """Test errata API with empty JSON."""
        with pytest.raises(Exception) as context:
            self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_EMPTY)
        assert "'errata_list' is a required property" in str(context)

    def test_empty_errata_list(self):
        """Test errata API with empty 'errata_list'."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_EMPTY_LIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_non_existing_errata(self):
        """Test errata API repsonse for non-existent errata."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON_NON_EXIST)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_schema(self):
        """Test schema of valid errata API response."""
        response = self.errata_api.process_list(api_version="v1", data=ERRATA_JSON)
        assert schemas.errata_schema.validate(response)

    @pytest.mark.skip("Blocked by https://github.com/RedHatInsights/vmaas/issues/419")
    def test_modified_since(self):
        """Test errata API with 'modified_since' property."""
        errata = ERRATA_JSON.copy()
        errata["modified_since"] = str(datetime.datetime.now().replace(tzinfo=pytz.UTC))
        response = self.errata_api.process_list(api_version="v1", data=errata)
        assert tools.match(EMPTY_RESPONSE, response) is True

        # without modified date
        errata["errata_list"] = ["RHSA-W/O:MODIFIED"]
        response = self.errata_api.process_list(api_version="v1", data=errata)
        assert tools.match(EMPTY_RESPONSE, response) is True
