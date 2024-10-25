"""
Module to handle /repos API calls.
"""

import os
from collections import defaultdict

from vmaas.webapp.cache import (
    REPO_NAME,
    REPO_URL,
    REPO_BASEARCH,
    REPO_RELEASEVER,
    REPO_PRODUCT,
    REPO_REVISION,
    REPO_LAST_CHANGE,
    REPO_THIRD_PARTY,
    ERRATA_UPDATED,
    ERRATA_ID,
    ERRATA_PKGIDS,
    PKG_NAME_ID
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
        if not modified_since_dt or (repo_detail[REPO_LAST_CHANGE] is not None and
                                     repo_detail[REPO_LAST_CHANGE] > modified_since_dt):
            return True
        return False

    @staticmethod
    def _errata_modified_since(errata_detail, modified_since_dt):
        if not modified_since_dt or (errata_detail[ERRATA_UPDATED] is not None and
                                     errata_detail[ERRATA_UPDATED] > modified_since_dt):
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

    def _get_updated_packages(self, repo_id, repoid2errataids):
        pkg_names = set()
        for errata_id in repoid2errataids[repo_id]:
            errata_name = self.cache.errataid2name[errata_id]
            errata = self.cache.errata_detail[errata_name]
            for pkg_id in errata[ERRATA_PKGIDS]:
                name_id = self.cache.package_details[pkg_id][PKG_NAME_ID]
                pkg_names.add(self.cache.id2packagename[name_id])
        return list(pkg_names)

    def _build_repoid2errataids(self, modified_since_dt):
        repoid2errataids = defaultdict(list)
        if modified_since_dt:
            for errata in self.cache.errata_detail.values():
                if self._errata_modified_since(errata, modified_since_dt):
                    for repo_id in self.cache.errataid2repoids[errata[ERRATA_ID]]:
                        repoid2errataids[repo_id].append(errata[ERRATA_ID])
        return repoid2errataids

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data.get('repository_list', None)
        strip_prefixes(repos, REPO_PREFIXES)
        modified_since = data.get('modified_since', None)
        show_packages = data.get("show_packages", False)
        modified_since_dt = parse_datetime(modified_since)
        has_packages = data.get("has_packages", False)
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

        repoid2errataids = self._build_repoid2errataids(modified_since_dt)

        actual_page_size = 0
        repo_page_to_process, pagination_response = paginate(repos, page, page_size, filters=filters)
        latest_repo_change = None
        for label in repo_page_to_process:
            cs_id = self.cache.label2content_set_id[label]
            for repo_id in self.cache.repolabel2ids.get(label, []):
                repo_detail = self.cache.repo_detail[repo_id]
                if not modified_since_dt or self._modified_since(repo_detail, modified_since_dt):
                    if repo_id in self.cache.repo_id2cpe_ids:
                        cpe_ids = self.cache.repo_id2cpe_ids[repo_id]
                    else:
                        cpe_ids = self.cache.content_set_id2cpe_ids.get(cs_id, [])

                    repo = {
                        "label": label,
                        "name": repo_detail[REPO_NAME],
                        "url": repo_detail[REPO_URL],
                        "basearch": none2empty(repo_detail[REPO_BASEARCH]),
                        "releasever": none2empty(repo_detail[REPO_RELEASEVER]),
                        "product": repo_detail[REPO_PRODUCT],
                        "revision": format_datetime(repo_detail[REPO_REVISION]),
                        "last_change": format_datetime(repo_detail[REPO_LAST_CHANGE]),
                        "cpes": [self.cache.cpe_id2label[cpe_id] for cpe_id in cpe_ids],
                        "third_party": repo_detail[REPO_THIRD_PARTY]
                    }
                    updated_packages = self._get_updated_packages(repo_id, repoid2errataids)
                    if show_packages:
                        repo["updated_package_names"] = updated_packages
                    # Skip repository in the output if there are no changed packages found
                    # (There have to be some modified_since and has_packages flag enabled)
                    if updated_packages or not modified_since_dt or not has_packages:
                        repolist.setdefault(label, []).append(repo)
                    if not latest_repo_change or repo_detail[REPO_LAST_CHANGE] > latest_repo_change:
                        latest_repo_change = repo_detail[REPO_LAST_CHANGE]
            actual_page_size += len(repolist.get(label, []))

        response = {
            'repository_list': repolist,
            'latest_repo_change': format_datetime(latest_repo_change) if latest_repo_change else None,
            'last_change': format_datetime(self.cache.dbchange['last_change'])
        }

        pagination_response['page_size'] = actual_page_size
        response.update(pagination_response)

        return response
