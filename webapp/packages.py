"""
Module to handle /packages API calls.
"""

from jsonschema import validate

from cache import REPO_LABEL, REPO_NAME, REPO_BASEARCH, REPO_RELEASEVER
from utils import split_packagename

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

    def process_list(self, data):
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

        for pkg in packages:
            packagedata = packagelist.setdefault(pkg, {})
            name, epoch, ver, rel, arch = split_packagename(pkg)
            if name in self.cache.packagename2id \
               and (epoch, ver, rel) in self.cache.evr2id \
               and arch in self.cache.arch2id:
                name_id = self.cache.packagename2id[name]
                evr_id = self.cache.evr2id[(epoch, ver, rel)]
                arch_id = self.cache.arch2id[arch]
                if (name_id, evr_id, arch_id) in self.cache.nevra2pkgid:
                    pkg_id = self.cache.nevra2pkgid[(name_id, evr_id, arch_id)]
                    packagedata['summary'] = self.cache.package_details[pkg_id][3]
                    packagedata['description'] = self.cache.package_details[pkg_id][4]
                    packagedata['repositories'] = []
                    for repo_id in self.cache.pkgid2repoids[pkg_id]:
                        repodetail = self.cache.repo_detail[repo_id]
                        repodata = {
                            'label': repodetail[REPO_LABEL],
                            'name': repodetail[REPO_NAME],
                            'basearch': repodetail[REPO_BASEARCH],
                            'releasever': repodetail[REPO_RELEASEVER]
                        }
                        packagedata['repositories'].append(repodata)
        response = {
            'package_list': packagelist
        }

        return response
