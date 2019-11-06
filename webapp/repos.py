"""
Module to handle /repos API calls.
"""

import re

from cache import REPO_NAME, REPO_URL, REPO_BASEARCH, REPO_RELEASEVER, REPO_PRODUCT, REPO_REVISION
from common.webapp_utils import paginate, none2empty, parse_datetime, filter_item_if_exists


class RepoAPI:
    """ Main /repos API class."""

    def __init__(self, cache):
        self.cache = cache

    def find_repos_by_regex(self, repo_regex):
        """
        Returns list of repositories (content_set labels) matching a provided regex

        :param repo_regex: string containing a POSIX regular expression

        :returns: list of repository-labels matching the provided regex
        """
        if not repo_regex.startswith('^'):
            repo_regex = '^' + repo_regex

        if not repo_regex.endswith('$'):
            repo_regex = repo_regex + '$'

        return [label for label in self.cache.repolabel2ids if re.match(repo_regex, label)]

    @staticmethod
    def _modified_since(repo_detail, modified_since_dt):
        if not modified_since_dt or (repo_detail[REPO_REVISION] != 'None' and parse_datetime(
                repo_detail[REPO_REVISION]) > modified_since_dt):
            return True
        return False

    def _filter_modified_since(self, repos_to_process, modified_since_dt):
        """Filter repositories by modified since"""
        filtered_repos_to_process = []
        for label in repos_to_process:
            for repo_id in self.cache.repolabel2ids.get(label, []):
                repo_detail = self.cache.repo_detail[repo_id]
                if not modified_since_dt or self._modified_since(repo_detail, modified_since_dt):
                    filtered_repos_to_process.append(label)
                    break
        return filtered_repos_to_process

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data.get('repository_list', None)
        modified_since = data.get('modified_since', None)
        modified_since_dt = parse_datetime(modified_since)
        page = data.get("page", None)
        page_size = data.get("page_size", None)
        repolist = {}
        if not repos:
            return repolist

        filters = []
        if modified_since:
            filters.append((self._filter_modified_since, [modified_since_dt]))

        if len(repos) == 1:
            # treat single-label like a regex, get all matching names
            repos = self.find_repos_by_regex(repos[0])

        repos = list(set(repos))

        repo_details = {}
        for label in repos:
            for repo_id in self.cache.repolabel2ids.get(label, []):
                repo_details[label] = self.cache.repo_detail[repo_id]
        filters.append((filter_item_if_exists, [repo_details]))

        actual_page_size = 0
        repo_page_to_process, pagination_response = paginate(repos, page, page_size, filters=filters)
        for label in repo_page_to_process:
            for repo_id in self.cache.repolabel2ids.get(label, []):
                repo_detail = self.cache.repo_detail[repo_id]
                if not modified_since_dt or self._modified_since(repo_detail, modified_since_dt):
                    repolist.setdefault(label, []).append({
                        "label": label,
                        "name": repo_detail[REPO_NAME],
                        "url": repo_detail[REPO_URL],
                        "basearch": none2empty(repo_detail[REPO_BASEARCH]),
                        "releasever": none2empty(repo_detail[REPO_RELEASEVER]),
                        "product": repo_detail[REPO_PRODUCT],
                        "revision": repo_detail[REPO_REVISION]
                    })
            actual_page_size += len(repolist[label])

        response = {
            'repository_list': repolist,
        }

        pagination_response['page_size'] = actual_page_size
        response.update(pagination_response)
        if modified_since:
            response["modified_since"] = modified_since

        return response
