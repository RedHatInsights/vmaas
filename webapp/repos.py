"""
Module to handle /repos API calls.
"""

import re

from cache import REPO_NAME, REPO_URL, REPO_BASEARCH, REPO_RELEASEVER, REPO_PRODUCT, REPO_REVISION


class RepoAPI(object):
    """ Main /repos API class."""
    def __init__(self, cache):
        self.cache = cache

    def find_repos_by_regex(self, repo_regex):
        """
        Returns list of repositories (content_set labels) matching a provided regex

        :param repo_regex: string containing a POSIX regular expression

        :returns: list of repository-labels matching the provided regex
        """
        return [label for label in self.cache.repolabel2ids if re.match(repo_regex, label)]

    def process_list(self, data):
        """
        Returns repository details.

        :param data: json request parsed into data structure

        :returns: json response with repository details
        """
        repos = data.get('repository_list', None)
        repolist = {}
        if not repos:
            return repolist

        if len(repos) == 1:
            # treat single-label like a regex, get all matching names
            repos = self.find_repos_by_regex(repos[0])

        for label in repos:
            for repo_id in self.cache.repolabel2ids[label]:
                repo_detail = self.cache.repo_detail[repo_id]
                repolist.setdefault(label, []).append({
                    "label": label,
                    "name": repo_detail[REPO_NAME],
                    "url": repo_detail[REPO_URL],
                    "basearch": repo_detail[REPO_BASEARCH],
                    "releasever": repo_detail[REPO_RELEASEVER],
                    "product": repo_detail[REPO_PRODUCT],
                    "revision": repo_detail[REPO_REVISION]
                    })

        response = {
            'repository_list': repolist,
        }

        return response
