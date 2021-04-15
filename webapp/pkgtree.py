"""
Module to handle /pkgtree API calls.
"""

from natsort import natsorted  # pylint: disable=E0401

from cache import PKG_NAME_ID, ERRATA_ISSUED, ERRATA_CVE, REPO_LABEL, REPO_NAME, \
    REPO_BASEARCH, REPO_RELEASEVER, REPO_REVISION, REPO_THIRD_PARTY, ERRATA_THIRD_PARTY
from common.dateutil import parse_datetime
from common.webapp_utils import format_datetime, none2empty, try_expand_by_regex
from common.rpm import join_rpm_name


class PkgtreeAPI:
    """ Main /packages API class."""
    def __init__(self, cache):
        self.cache = cache

    def _get_packages(self, pkgname_id):
        pkg_ids = set()
        # FIXME this implementation is not effecitve to traverse all items in package_details.
        #       Better implementation would require updates in the vmaas.dbm file format
        #       to contain some mapping from package_name to NEVRA or EVR or package_details.
        for pkg_id, pkg_val in self.cache.package_details.items():
            if pkgname_id == pkg_val[PKG_NAME_ID]:
                pkg_ids.add(pkg_id)
        return pkg_ids

    def _build_nevra(self, pkg_id):
        name_id, evr_id, arch_id, _, _, _ = self.cache.package_details[pkg_id]
        name = self.cache.id2packagename[name_id]
        epoch, ver, rel = self.cache.id2evr[evr_id]
        arch = self.cache.id2arch[arch_id]
        return join_rpm_name(name, epoch, ver, rel, arch)

    def _get_erratas(self, pkg_id):
        erratas = []
        if pkg_id in self.cache.pkgid2errataids:
            errata_ids = self.cache.pkgid2errataids[pkg_id]
            for err_id in errata_ids:
                name = self.cache.errataid2name[err_id]
                detail = self.cache.errata_detail[name]
                issued = detail[ERRATA_ISSUED]
                cves = detail[ERRATA_CVE]
                # Skip third party errata
                if detail[ERRATA_THIRD_PARTY]:
                    continue
                errata = {
                    'name': name,
                    'issued': none2empty(format_datetime(issued))}
                if cves:
                    errata['cve_list'] = natsorted(cves)
                erratas.append(errata)
        return natsorted(erratas, key=lambda err_dict: err_dict['name'])

    def _get_repositories(self, pkg_id):
        # FIXME Add support for modules and streams.
        repos = []
        if pkg_id in self.cache.pkgid2repoids:
            for repo_id in self.cache.pkgid2repoids[pkg_id]:
                detail = self.cache.repo_detail[repo_id]
                # Skip third party repos
                if detail[REPO_THIRD_PARTY]:
                    continue
                repos.append({
                    'label': detail[REPO_LABEL],
                    'name': detail[REPO_NAME],
                    'basearch': none2empty(detail[REPO_BASEARCH]),
                    'releasever': none2empty(detail[REPO_RELEASEVER]),
                    'revision': format_datetime(detail[REPO_REVISION])
                })
        return natsorted(repos, key=lambda repo_dict: repo_dict['label'])

    @staticmethod
    def _get_first_published_from_erratas(erratas):  # pylint: disable=R0201
        # 'first_published' is the 'issued' date of the oldest errata.
        first_published = None
        for ert in erratas:
            issued = parse_datetime(ert['issued'])
            if first_published is None or issued < first_published:
                first_published = issued
        return format_datetime(first_published)

    def try_expand_by_regex(self, names: list) -> list:
        """Expand list with a POSIX regex if possible"""
        out_names = try_expand_by_regex(names, self.cache.packagename2id)
        return out_names

    def _get_pkg_item(self, pkg_id: int) -> dict:
        pkg_nevra = self._build_nevra(pkg_id)
        errata = self._get_erratas(pkg_id)
        repositories = self._get_repositories(pkg_id)
        # Skip content with no repos and no erratas (Should skip third party content)
        first_published = self._get_first_published_from_erratas(errata)
        pkg_item = {
            "nevra": pkg_nevra,
            "first_published": none2empty(first_published),
            "repositories": none2empty(repositories),
            "errata": none2empty(errata),
        }
        return pkg_item

    def _get_name_packages(self, name: str) -> list:
        pkgtree_list = []
        if name in self.cache.packagename2id:
            name_id = self.cache.packagename2id[name]
            pkg_ids = self._get_packages(name_id)
            for pkg_id in pkg_ids:
                pkg_item = self._get_pkg_item(pkg_id)
                pkgtree_list.append(pkg_item)
        pkgtree_list = natsorted(pkgtree_list, key=lambda nevra_list: nevra_list['nevra'])
        return pkgtree_list

    def _build_package_name_list(self, names: list) -> dict:
        package_name_list = dict()
        for name in names:
            pkgtree_list = self._get_name_packages(name)
            package_name_list[name] = pkgtree_list
        return package_name_list

    def process_list(self, api_version: int, data: dict):  # pylint: disable=unused-argument
        """
        Returns list of NEVRAs for given packge name.

        :param data: json request parsed into data structure
        :param api_version: API version (1, 2, 3).
        :returns: json response with list of NEVRAs
        """

        # Date and time of last data change in the VMaaS DB
        last_change = format_datetime(self.cache.dbchange['last_change'])

        names = data.get('package_name_list', None)
        if not names:
            return dict()

        if api_version >= 3:
            names = self.try_expand_by_regex(names)

        package_name_list = self._build_package_name_list(names)

        response = {
            'package_name_list': package_name_list,
            'last_change': last_change,
        }

        return response
