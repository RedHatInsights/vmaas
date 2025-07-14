"""
Module to handle /pkgtree API calls.
"""

import datetime
from natsort import natsorted  # pylint: disable=E0401

from vmaas.webapp.cache import PKG_NAME_ID, ERRATA_ISSUED, ERRATA_CVE, REPO_LABEL, REPO_NAME, \
    REPO_BASEARCH, REPO_RELEASEVER, REPO_REVISION, REPO_THIRD_PARTY, ERRATA_THIRD_PARTY, ERRATA_UPDATED, \
    PKG_SUMMARY_ID, PKG_DESC_ID
from vmaas.common.date_utils import parse_datetime as parse_dt
from vmaas.common.webapp_utils import format_datetime, none2empty, try_expand_by_regex, paginate, parse_datetime
from vmaas.common.rpm_utils import join_rpm_name


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

    def _build_nevra(self, pkg_detail: tuple):
        name_id, evr_id, arch_id, _, _, _, _ = pkg_detail
        name = self.cache.id2packagename[name_id]
        epoch, ver, rel = self.cache.id2evr[evr_id]
        arch = self.cache.id2arch[arch_id]
        return join_rpm_name(name, epoch, ver, rel, arch)

    @staticmethod
    def _update_modified_found(modified_found_prev: bool, modified_since: datetime.datetime,
                               updated_ts: datetime.datetime) -> bool:
        if modified_found_prev:
            return True
        if modified_since is None or updated_ts is None:
            return False
        if updated_ts >= modified_since:
            return True
        return False

    def _get_erratas(self, api_version: int, pkg_id: int, modified_since: datetime.datetime,
                     third_party: bool) -> tuple:
        erratas = []
        modified_found = False
        if pkg_id in self.cache.pkgid2errataids:
            errata_ids = self.cache.pkgid2errataids[pkg_id]
            for err_id in errata_ids:
                name = self.cache.errataid2name[err_id]
                detail = self.cache.errata_detail[name]
                if detail[ERRATA_THIRD_PARTY] and not third_party:
                    continue
                issued = detail[ERRATA_ISSUED]
                errata = {'name': name,
                          'issued': none2empty(format_datetime(issued))}
                if api_version >= 3:
                    updated_ts = detail[ERRATA_UPDATED]
                    errata['updated'] = none2empty(format_datetime(updated_ts))
                    modified_found = self._update_modified_found(modified_found, modified_since, updated_ts)
                cves = detail[ERRATA_CVE]
                if cves:
                    errata['cve_list'] = natsorted(cves)
                erratas.append(errata)
        erratas = natsorted(erratas, key=lambda err_dict: err_dict['name'])
        return erratas, modified_found

    def _get_repositories(self, pkg_id) -> tuple:
        # FIXME Add support for modules and streams.
        repos = []
        third_party_flags = []
        if pkg_id in self.cache.pkgid2repoids:
            for repo_id in self.cache.pkgid2repoids[pkg_id]:
                detail = self.cache.repo_detail[repo_id]
                third_party_flags.append(detail[REPO_THIRD_PARTY])
                repos.append({
                    'label': detail[REPO_LABEL],
                    'name': detail[REPO_NAME],
                    'basearch': none2empty(detail[REPO_BASEARCH]),
                    'releasever': none2empty(detail[REPO_RELEASEVER]),
                    'revision': format_datetime(detail[REPO_REVISION])
                })

        # Check whether all found repositories are third-party
        third_party_only = (len(third_party_flags) > 0) and (False not in third_party_flags)
        return natsorted(repos, key=lambda repo_dict: repo_dict['label']), third_party_only

    @staticmethod
    def _get_first_published_from_erratas(erratas):
        # 'first_published' is the 'issued' date of the oldest errata.
        first_published = None
        for ert in erratas:
            issued = parse_dt(ert['issued'])
            if first_published is None or issued < first_published:
                first_published = issued
        return format_datetime(first_published)

    def try_expand_by_regex(self, api_version: int, names: list) -> list:
        """Expand list with a POSIX regex if possible"""
        if api_version >= 3:
            out_names = try_expand_by_regex(names, self.cache.packagename2id)
            return out_names
        return names

    def _get_cached_string(self, pkg_detail: tuple, field_id: int) -> str:
        str_id = pkg_detail[field_id]
        cached_str = self.cache.strings.get(str_id, None)
        return cached_str

    @staticmethod
    def _exclude_not_modified(modified: bool, modified_since: datetime.datetime, n_erratas: int) -> bool:
        if n_erratas == 0 and modified_since is not None:  # Skip packages without time info when "modified_since" used
            return True
        if modified_since is None:  # Include all packages when "modified_since" not used
            return False
        if not modified:  # Exclude not-modified packages ("modified_since" used)
            return True
        return False  # Include all packages by default

    def _update_repositories(self, pkg_id: int, opts: dict) -> tuple:
        """Check whether all repos are 'third-party' to exclude package if third-party=True is set."""
        if opts["return_repositories"]:
            repositories, third_party_only = self._get_repositories(pkg_id)
            return {"repositories": none2empty(repositories)}, third_party_only
        return {}, False

    def _update_errata(self, api_version: int, pkg_id: int, opts: dict, third_party: bool) -> tuple:
        """Add errata-related data, skip based on modified_since if needed"""
        data = {}
        if opts["return_errata"] or opts["modified_since"] is not None:
            errata, modified = self._get_erratas(api_version, pkg_id, opts["modified_since"], third_party)
            if self._exclude_not_modified(modified, opts["modified_since"], len(errata)):
                return None, True
            if opts["return_errata"]:
                data["errata"] = none2empty(errata)
                first_published = self._get_first_published_from_erratas(errata)
                data["first_published"] = none2empty(first_published)
        return data, False

    def _update_summary_desc(self, api_version: int, pkg_detail: tuple, opts: dict) -> dict:
        data = {}
        if api_version >= 3:
            if opts["return_summary"]:
                data["summary"] = self._get_cached_string(pkg_detail, PKG_SUMMARY_ID)
            if opts["return_description"]:
                data["description"] = self._get_cached_string(pkg_detail, PKG_DESC_ID)
        return data

    def _get_pkg_item(self, api_version: int, pkg_id: int, opts: dict, third_party: bool) -> dict:
        pkg_detail = self.cache.package_details[pkg_id]
        pkg_nevra = self._build_nevra(pkg_detail)
        # Skip content with no repos and no erratas (Should skip third party content)
        pkg_item = {
            "nevra": pkg_nevra,
        }
        repositories, third_party_only = self._update_repositories(pkg_id, opts)
        if not third_party and third_party_only:  # All repos are "third-party" and "third-party" not set, exclude pkg.
            return None
        pkg_item.update(repositories)
        errata_update, modified_since_skip = self._update_errata(api_version, pkg_id, opts, third_party)
        if modified_since_skip:
            return None
        pkg_item.update(errata_update)
        summary_desc_update = self._update_summary_desc(api_version, pkg_detail, opts)
        pkg_item.update(summary_desc_update)
        return pkg_item

    def _get_name_packages(self, api_version: int, name: str, opts: dict, third_party: bool) -> list:
        pkgtree_list = []
        if name in self.cache.packagename2id:
            name_id = self.cache.packagename2id[name]
            pkg_ids = self._get_packages(name_id)
            for pkg_id in pkg_ids:
                pkg_item = self._get_pkg_item(api_version, pkg_id, opts, third_party)
                if pkg_item is not None:
                    pkgtree_list.append(pkg_item)
        pkgtree_list = natsorted(pkgtree_list, key=lambda nevra_list: nevra_list['nevra'])
        return pkgtree_list

    @staticmethod
    def _get_third_party(api_version: int, opts: dict) -> bool:
        """Third party is disabled by default, allowed only for API v3"""
        if api_version >= 3 and opts["third_party"]:
            return True
        return False

    def _build_package_name_list(self, api_version: int, names: list, opts: dict) -> dict:
        package_name_list = {}
        third_party = self._get_third_party(api_version, opts)
        for name in names:
            pkgtree_list = self._get_name_packages(api_version, name, opts, third_party)
            package_name_list[name] = pkgtree_list
        return package_name_list

    @staticmethod
    def _use_pagination(api_version: int, names: list, page: int, page_size: int):
        if api_version >= 3:
            names_page, pagination_response = paginate(names, page, page_size)
            return names_page, pagination_response
        return names, {}

    def process_list(self, api_version: int, data: dict):  # pylint: disable=unused-argument
        """
        Returns list of NEVRAs for given packge name.

        :param data: json request parsed into data structure
        :param api_version: API version (1, 2, 3).
        :returns: json response with list of NEVRAs
        """

        page = data.get("page", None)
        page_size = data.get("page_size", None)
        opts = {
            "modified_since": parse_datetime(data.get("modified_since", None)),
            "return_repositories": data.get("return_repositories", True),
            "return_errata": data.get("return_errata", True),
            "return_summary": data.get("return_summary", False),
            "return_description": data.get("return_description", False),
            "third_party": data.get("third_party", False),
        }

        names = data.get('package_name_list', None)
        if not names:
            return {}

        names = self.try_expand_by_regex(api_version, names)
        names, response = self._use_pagination(api_version, names, page, page_size)
        package_name_list = self._build_package_name_list(api_version, names, opts)
        response['package_name_list'] = package_name_list
        # Date and time of last data change in the VMaaS DB
        response['last_change'] = format_datetime(self.cache.dbchange['last_change'])
        return response
