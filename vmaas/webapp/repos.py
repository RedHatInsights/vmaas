"""
Module to handle /repos API calls.
"""

import os

from vmaas.webapp.cache import (
    REPO_NAME,
    REPO_URL,
    REPO_BASEARCH,
    REPO_RELEASEVER,
    REPO_PRODUCT,
    REPO_REVISION,
    REPO_THIRD_PARTY
)
from vmaas.common.date_utils import format_datetime
from vmaas.common.webapp_utils import paginate, none2empty, parse_datetime, \
    filter_item_if_exists, try_expand_by_regex, strip_prefixes

REPO_PREFIXES = os.getenv("REPO_NAME_PREFIXES", "").split(",")


class RepoAPI:
    """ Main /repos API class."""

    def __init__(self, cache):
        self.cache = cache

    @staticmethod
    def _modified_since(repo_detail, modified_since_dt):
        if not modified_since_dt or (repo_detail[REPO_REVISION] is not None and
                                     repo_detail[REPO_REVISION] > modified_since_dt):
            return True
        return False

    def try_expand_by_regex(self, repos: list) -> list:
        """Expand list with a POSIX regex if possible"""
        out_repos = try_expand_by_regex(repos, self.cache.repolabel2ids)
        return out_repos

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

    def _filter_third_party(self, repos_to_process, include_third_party):
        if include_third_party:
            return repos_to_process

        filtered_repos = []
        for label in repos_to_process:
            should_add = True
            for repo_id in self.cache.repolabel2ids.get(label, []):
                repo_detail = self.cache.repo_detail[repo_id]
                # If we don't want third party repo, and this repo is flagged as third party, skip it
                if repo_detail[REPO_THIRD_PARTY]:
                    should_add = False
            if should_add:
                filtered_repos.append(label)
        return filtered_repos

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data.get('repository_list', None)
        strip_prefixes(repos, REPO_PREFIXES)
        modified_since = data.get('modified_since', None)
        modified_since_dt = parse_datetime(modified_since)
        page = data.get("page", None)
        page_size = data.get("page_size", None)

        # By default, don't include third party data
        want_third_party = data.get('third_party', False)

        repolist = {}
        if not repos:
            return repolist

        filters = []
        if modified_since:
            filters.append((self._filter_modified_since, [modified_since_dt]))

        filters.append((self._filter_third_party, [want_third_party]))

        repos = self.try_expand_by_regex(repos)

        repos = list(set(repos))

        repo_details = {}
        for label in repos:
            for repo_id in self.cache.repolabel2ids.get(label, []):
                repo_details[label] = self.cache.repo_detail[repo_id]
        filters.append((filter_item_if_exists, [repo_details]))

        actual_page_size = 0
        repo_page_to_process, pagination_response = paginate(repos, page, page_size, filters=filters)
        for label in repo_page_to_process:
            cs_id = self.cache.label2content_set_id[label]
            for repo_id in self.cache.repolabel2ids.get(label, []):
                repo_detail = self.cache.repo_detail[repo_id]
                if not modified_since_dt or self._modified_since(repo_detail, modified_since_dt):
                    if repo_id in self.cache.repo_id2cpe_ids:
                        cpe_ids = self.cache.repo_id2cpe_ids[repo_id]
                    else:
                        cpe_ids = self.cache.content_set_id2cpe_ids.get(cs_id, [])
                    repolist.setdefault(label, []).append({
                        "label": label,
                        "name": repo_detail[REPO_NAME],
                        "url": repo_detail[REPO_URL],
                        "basearch": none2empty(repo_detail[REPO_BASEARCH]),
                        "releasever": none2empty(repo_detail[REPO_RELEASEVER]),
                        "product": repo_detail[REPO_PRODUCT],
                        "revision": format_datetime(repo_detail[REPO_REVISION]),
                        "cpes": [self.cache.cpe_id2label[cpe_id] for cpe_id in cpe_ids],
                        "third_party": repo_detail[REPO_THIRD_PARTY]
                    })
            actual_page_size += len(repolist[label])

        response = {
            'repository_list': repolist,
            'last_change': format_datetime(self.cache.dbchange['last_change'])
        }

        pagination_response['page_size'] = actual_page_size
        response.update(pagination_response)

        return response
