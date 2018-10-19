"""Unit test for CveAPI module."""
from test import schemas
from test.conftest import TestBase

import pytest

from repos import RepoAPI

REPO_JSON_EMPTY = {}
REPO_JSON_BAD = {"page_size": 9}
REPO_JSON = {"repository_list": ["rhel-7-server-rpms"]}
REPO_JSON_EMPTY_LIST = {"repository_list": [""]}
REPO_JSON_NON_EXIST = {"repository_list": ["non-existent-repo"]}

EMPTY_RESPONSE = {"repository_list": {}, "page": 1, "page_size": 5000, "pages": 0}


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
        assert self.repo.find_repos_by_regex("rhel-7-server-rpms") == ["rhel-7-server-rpms"]
        assert "rhel-7-server-rpms" in self.repo.find_repos_by_regex("rhel-[7].*")

    def test_wrong_regex(self):
        """Test wrong repos regex."""
        with pytest.raises(Exception) as context:
            self.repo.find_repos_by_regex("*")
        assert "nothing to repeat" in str(context)

    def test_missing_required(self):
        """Test missing required property 'repository_list'."""
        with pytest.raises(Exception) as context:
            self.repo.process_list(api_version="v1", data=REPO_JSON_BAD)
        assert "'repository_list' is a required property" in str(context)

    def test_empty_json(self):
        """Test repos API with empty JSON."""
        with pytest.raises(Exception) as context:
            self.repo.process_list(api_version="v1", data=REPO_JSON_EMPTY)
        assert "'repository_list' is a required property" in str(context)

    def test_empty_repository_list(self):
        """Test repos API with empty 'repository_list'."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_EMPTY_LIST)
        assert response == EMPTY_RESPONSE

    def test_non_existing_repo(self):
        """Test repos API repsonse for non-existent repo."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON_NON_EXIST)
        assert response == EMPTY_RESPONSE

    def test_schema(self):
        """Test schema of valid repos API response."""
        response = self.repo.process_list(api_version="v1", data=REPO_JSON)
        assert schemas.repos_schema.validate(response)
