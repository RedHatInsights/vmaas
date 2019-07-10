"""
Module to handle /packages API calls.
"""

import re
from jsonschema import validate

from cache import REPO_LABEL, REPO_NAME, REPO_BASEARCH, REPO_RELEASEVER, PKG_SUMMARY, PKG_DESC, PKG_SOURCE_PKG_ID
import utils

JSON_SCHEMA = {
    'type' : 'object',
    'required': ['package_list'],
    'properties' : {
        'package_list': {
            'type': 'array', 'items': {'type': 'string'}, 'minItems' : 1
            },
    }
}


class PackagesAPI:
    """ Main /packages API class."""
    def __init__(self, cache):
        self.cache = cache

    def find_packages_by_regex(self, regex):
        """Returns list of packages matching a provided regex."""
        name, epoch, ver, rel, arch = utils.split_packagename(regex)

        if name and epoch and ver and rel and arch and not regex[-2:] == '.*':
            # If there is no regular expression return all packages what we get in api request
            return [regex]

        if not regex.startswith('^'):
            regex = '^' + regex

        if not regex.endswith('$'):
            regex = regex + '$'

        filtered_pkgs = []
        for (name_id, evr_id, arch_id) in self.cache.nevra2pkgid:
            pkg_id = self.cache.nevra2pkgid[(name_id, evr_id, arch_id)]
            package_list = self._get_built_binary_packages(pkg_id)
            for pkg in package_list:
                if re.match(regex, pkg):
                    filtered_pkgs.append(pkg)
        return filtered_pkgs

    def _get_source_package(self, pkg_detail):
        src_pkg_id = pkg_detail[PKG_SOURCE_PKG_ID]
        if src_pkg_id is not None:
            src_pkg_detail = self.cache.package_details[src_pkg_id]
            src_pkg_nevra = utils.pkg_detail2nevra(self.cache, src_pkg_detail)
            return src_pkg_nevra
        return None

    def _get_built_binary_packages(self, pkg_id: int) -> list:
        if pkg_id in self.cache.src_pkg_id2pkg_ids:
            ids = self.cache.src_pkg_id2pkg_ids[pkg_id]
            pkgs_list, source_pkgs_list = utils.pkgidlist2packages(self.cache, ids)
            return pkgs_list + source_pkgs_list
        return []

    def process_list(self, api_version, data): # pylint: disable=unused-argument
        """
        Returns package details.

        :param data: json request parsed into data structure

        :returns: json response with package details
        """
        validate(data, JSON_SCHEMA)

        packages = data.get('package_list', None)
        packagelist = {}
        if not packages:
            return packagelist

        if len(packages) == 1:
            # treat single-label like a regex, get all matching names
            packages = self.find_packages_by_regex(packages[0])

        for pkg in packages:
            packagedata = packagelist.setdefault(pkg, {})
            name, epoch, ver, rel, arch = utils.split_packagename(pkg)
            if name in self.cache.packagename2id \
               and (epoch, ver, rel) in self.cache.evr2id \
               and arch in self.cache.arch2id:
                name_id = self.cache.packagename2id[name]
                evr_id = self.cache.evr2id[(epoch, ver, rel)]
                arch_id = self.cache.arch2id[arch]
                if (name_id, evr_id, arch_id) in self.cache.nevra2pkgid:
                    pkg_id = self.cache.nevra2pkgid[(name_id, evr_id, arch_id)]
                    pkg_detail = self.cache.package_details[pkg_id]
                    packagedata['summary'] = pkg_detail[PKG_SUMMARY]
                    packagedata['description'] = pkg_detail[PKG_DESC]
                    packagedata['source_package'] = self._get_source_package(pkg_detail)
                    packagedata['repositories'] = []
                    packagedata['package_list'] = self._get_built_binary_packages(pkg_id)
                    if pkg_id in self.cache.pkgid2repoids:
                        for repo_id in self.cache.pkgid2repoids[pkg_id]:
                            repodetail = self.cache.repo_detail[repo_id]
                            repodata = {
                                'label': repodetail[REPO_LABEL],
                                'name': repodetail[REPO_NAME],
                                'basearch': utils.none2empty(repodetail[REPO_BASEARCH]),
                                'releasever': utils.none2empty(repodetail[REPO_RELEASEVER])
                            }
                            packagedata['repositories'].append(repodata)
        response = {
            'package_list': packagelist
        }

        return response
