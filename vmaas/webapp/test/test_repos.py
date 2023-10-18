"""Unit test for CveAPI module."""

import pytest

from vmaas.webapp.test import schemas, tools
from vmaas.webapp.test.conftest import TestBase
from vmaas.webapp.repos import RepoAPI

REPO_JSON_EMPTY = {}
REPO_JSON_BAD = {"page_size": 9}
REPO_JSON = {"repository_list": ["rhel-7-server-rpms"]}
REPO_JSON_ALL = {"repository_list": ["rhel-7-server-rpms", "third-party-repo1"]}
REPO_JSON_MODIFIED_SINCE = {
    "repository_list": ["rhel-7-server-rpms"],
    "modified_since": "2099-01-01T00:00:00+00:00"
}
REPO_JSON_EMPTY_LIST = {"repository_list": [""]}
REPO_JSON_NON_EXIST = {"repository_list": ["non-existent-repo"]}
REPO_JSON_WITH_PREFIX = {"repository_list": ["rhul-rhel-7-server-rpms"]}

EMPTY_RESPONSE = {"repository_list": {}, "page": 1, "page_size": 0, "pages": 0,
                  "last_change": "2019-03-07T09:17:23.799995+00:00",
                  "latest_repo_change": None}


class TestRepoAPI(TestBase):
    """Test RepoAPI class."""

    repo = None

    # pylint: disable=unused-argument
    @pytest.fixture(autouse=True)
    def setup_api(self, load_cache):
        """Set RepoAPI object."""
        self.repo = RepoAPI(self.cache)

    def test_regex(self):
        """Test correct repos regex."""
        assert self.repo.try_expand_by_regex(["rhel-7-server-rpms"]) == ["rhel-7-server-rpms"]
        assert "rhel-7-server-rpms" in self.repo.try_expand_by_regex(["rhel-[7].*"])

    def test_wrong_regex(self):
        """Test wrong repos regex."""
        with pytest.raises(Exception) as context:
            self.repo.try_expand_by_regex(["*"])
        assert "nothing to repeat" in str(context.value)

    def test_empty_repository_list(self):
        """Test repos API with empty 'repository_list'."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_EMPTY_LIST)
        assert response == EMPTY_RESPONSE

    def test_non_existing_repo(self):
        """Test repos API response for non-existent repo."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_NON_EXIST)
        assert response == EMPTY_RESPONSE

    def test_third_party(self):
        """Test filtering with third party enabled"""
        data = {**REPO_JSON_ALL, "third_party": True}
        response = self.repo.process_list(api_version="v1", data=data)
        assert len(response["repository_list"]) == 2

    def test_non_third_party(self):
        """Test filtering with third-party content disabled"""
        data = {**REPO_JSON_ALL}
        data.pop("third_party", None)
        response = self.repo.process_list(api_version="v1", data=data)
        assert len(response["repository_list"]) == 1

    def test_schema(self):
        """Test schema of valid repos API response."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON)
        assert schemas.repos_schema.validate(response)

    def test_modified_since(self):
        """Test repos API with 'modified_since' property."""
        response = self.repo.process_list(api_version=1, data=REPO_JSON_MODIFIED_SINCE)
        assert tools.match(EMPTY_RESPONSE, response) is True

    def test_page_size(self):
        """Test repos API page size"""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON)
        page_size = 0
        for label in response['repository_list']:
            page_size += len(response['repository_list'][label])
        assert response['page_size'] == page_size

    def test_page_size_mod_since(self):
        """Test repos API page size with 'modified_since' property"""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_MODIFIED_SINCE)
        page_size = 0
        for label in response['repository_list']:
            page_size += len(response['repository_list'][label])
        assert response['page_size'] == page_size

    def test_repo_with_prefix(self):
        """Test repos with valid prefixes"""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_WITH_PREFIX)
        assert len(response["repository_list"]) == 1
