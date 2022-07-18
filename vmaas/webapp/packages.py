"""
Module to handle /packages API calls.
"""

from vmaas.webapp.cache import REPO_LABEL, REPO_NAME, REPO_BASEARCH, REPO_RELEASEVER, PKG_SUMMARY_ID, PKG_DESC_ID, \
    PKG_SOURCE_PKG_ID, REPO_THIRD_PARTY
import vmaas.common.webapp_utils as utils
from vmaas.common.rpm_utils import parse_rpm_name


class PackagesAPI:
    """ Main /packages API class."""

    def __init__(self, cache):
        self.cache = cache

    def _get_source_package(self, pkg_detail):
        src_pkg_id = pkg_detail[PKG_SOURCE_PKG_ID]
        if src_pkg_id:
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

    def process_list(self, api_version, data):  # pylint: disable=unused-argument
        """
        Returns package details.

        :param data: json request parsed into data structure

        :returns: json response with package details
        """
        packages = data.get('package_list', None)
        # By default, don't include third party data
        want_third_party = data.get('third_party', False)

        packagelist = {}

        response = {
            'last_change': utils.format_datetime(self.cache.dbchange['last_change'])
        }

        if not packages:
            response['package_list'] = packagelist
            return response

        for pkg in packages:
            packagedata = packagelist.setdefault(pkg, {})
            is_third_party = False

            name, epoch, ver, rel, arch = parse_rpm_name(pkg, default_epoch='0')
            if name in self.cache.packagename2id \
                    and (epoch, ver, rel) in self.cache.evr2id \
                    and arch in self.cache.arch2id:
                name_id = self.cache.packagename2id[name]
                evr_id = self.cache.evr2id[(epoch, ver, rel)]
                arch_id = self.cache.arch2id[arch]
                pkg_id = self.cache.nevra2pkgid.get((name_id, evr_id, arch_id), None)
                if pkg_id:
                    pkg_detail = self.cache.package_details[pkg_id]
                    packagedata['summary'] = self.cache.strings.get(pkg_detail[PKG_SUMMARY_ID], None)
                    packagedata['description'] = self.cache.strings.get(pkg_detail[PKG_DESC_ID], None)
                    packagedata['source_package'] = self._get_source_package(pkg_detail)
                    packagedata['repositories'] = []
                    packagedata['package_list'] = self._get_built_binary_packages(pkg_id)
                    if pkg_id in self.cache.pkgid2repoids:
                        for repo_id in self.cache.pkgid2repoids[pkg_id]:
                            repodetail = self.cache.repo_detail[repo_id]
                            is_third_party = is_third_party or bool(repodetail[REPO_THIRD_PARTY])
                            repodata = {
                                'label': repodetail[REPO_LABEL],
                                'name': repodetail[REPO_NAME],
                                'basearch': utils.none2empty(repodetail[REPO_BASEARCH]),
                                'releasever': utils.none2empty(repodetail[REPO_RELEASEVER]),
                            }
                            packagedata['repositories'].append(repodata)

            # If the package is third party, then remove it from result
            if not want_third_party and is_third_party:
                packagelist[pkg] = {}

        response['package_list'] = packagelist
        return response
