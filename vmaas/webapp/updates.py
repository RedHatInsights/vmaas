"""
Module to handle /updates API calls.
"""
from typing import List, Set

import rpm

from vmaas.webapp. cache import REPO_LABEL, REPO_BASEARCH, REPO_RELEASEVER, REPO_URL, PKG_SUMMARY_ID, PKG_DESC_ID, \
    ERRATA_CVE, ERRATA_TYPE, PKG_EVR_ID, ERRATA_THIRD_PARTY
from vmaas.webapp.repos import REPO_PREFIXES
from vmaas.common.webapp_utils import none2empty, filter_package_list, format_datetime, strip_prefixes
from vmaas.common.rpm_utils import parse_rpm_name, join_rpm_name

SECURITY_ERRATA_TYPE = 'security'


def filter_non_security(errata_detail: dict, security_only: bool) -> bool:
    """Decide whether the errata should be filtered base on 'securiyt only' rule."""
    if not security_only:
        return False
    is_security = errata_detail[ERRATA_TYPE] == SECURITY_ERRATA_TYPE or errata_detail[ERRATA_CVE]
    return not is_security


def get_security_only(api_version: int, data: dict) -> bool:
    """Set 'security_only' flag based on input data and API version.
       For API version < 3 only security updates are provided."""
    if api_version < 3:
        security_only = True
    else:
        security_only = data.get("security_only", False)
    return security_only


def insert_if_not_empty(struct: dict, key: str, value) -> dict:
    """Insert value to the struct under the key, if the value is not None"""
    if value is not None:
        struct[key] = value
    return struct


class UpdatesAPI:
    """ Main /updates API class."""

    def __init__(self, db_cache):
        self.db_cache = db_cache  # DB dump in memory, stored like a dict

    def _get_repository_list(self, data: dict) -> (list, list):
        repo_list = data.get('repository_list', None)
        repo_paths = data.get('repository_paths', None)
        if repo_list is not None:
            strip_prefixes(repo_list, REPO_PREFIXES)
            repo_ids = []
            for label in repo_list:
                repo_id = self.db_cache.repolabel2ids.get(label, None)
                if repo_id:
                    repo_ids.extend(repo_id)
        elif repo_paths is None:
            repo_ids = list(self.db_cache.repo_detail.keys())
        else:
            repo_ids = []
        return repo_list, repo_ids

    def _get_repository_paths(self, data: dict, repo_ids: list) -> (list, list):
        repo_paths = data.get('repository_paths', None)
        if repo_paths is not None:
            for repo_path in repo_paths:
                if not repo_path:
                    continue

                repo_id = self.db_cache.repopath2ids.get(repo_path.rstrip('/'), None)
                if repo_id:
                    repo_ids.extend(repo_id)
        return repo_paths, repo_ids

    def _get_releasever(self, data: dict, repo_ids: list) -> (str, list):
        releasever = data.get('releasever', None)
        if releasever is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.db_cache.repo_detail[oid][REPO_RELEASEVER] == releasever
                        or (self.db_cache.repo_detail[oid][REPO_RELEASEVER] is None
                            and releasever in self.db_cache.repo_detail[oid][REPO_URL])]
        return releasever, repo_ids

    def _get_basearch(self, data: dict, repo_ids: list) -> (str, set):
        basearch = data.get('basearch', None)
        if basearch is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.db_cache.repo_detail[oid][REPO_BASEARCH] == basearch
                        or (self.db_cache.repo_detail[oid][REPO_BASEARCH] is None
                            and basearch in self.db_cache.repo_detail[oid][REPO_URL])]
        repo_ids = set(repo_ids)
        return basearch, repo_ids

    def _get_modules_list(self, data: dict) -> (list, set):
        modules_list_arr = data.get('modules_list', [])
        module_info = [(x['module_name'], x['module_stream']) for x in modules_list_arr]
        module_ids = set()
        for module in module_info:
            if module in self.db_cache.modulename2id:
                module_ids.update(self.db_cache.modulename2id[module])
        # filter out streams without satisfied requires
        filtered_ids = set()
        for stream_id in module_ids:
            requires = self.db_cache.modulerequire.get(stream_id, set())
            if requires.issubset(module_ids):
                filtered_ids.add(stream_id)
        modules_list = data.get('modules_list', None)
        return modules_list, filtered_ids

    def process_input_packages(self, data: dict) -> (dict, dict):
        """Parse input NEVRAs and filter out unknown (or without updates) package names."""
        latest_only = data.get("latest_only", False)
        packages_to_process = filter_package_list(data.get('package_list', None), latest_only)
        filtered_packages_to_process = {}
        update_list = {}
        if packages_to_process is not None:
            for pkg in packages_to_process:
                update_list[pkg] = {}
                name, epoch, ver, rel, arch = parse_rpm_name(pkg, default_epoch='0')
                if name in self.db_cache.packagename2id:
                    if self.db_cache.packagename2id[name] in self.db_cache.updates_index:
                        filtered_packages_to_process[pkg] = {'parsed_nevra': (name, epoch, ver, rel, arch)}
        return filtered_packages_to_process, update_list

    def _repos_by_pkgs(self, pkg_ids: List[int], repo_ids: Set[int]) -> Set[int]:
        res = set()
        for pkg_id in pkg_ids:
            res.update([x for x in self.db_cache.pkgid2repoids.get(pkg_id, []) if x in repo_ids])
        return res

    def _get_repositories(self, errata_id: int, available_repo_ids: set) -> set:
        repo_ids = set()
        errata_repo_ids = set()
        errata_repo_ids.update(self.db_cache.errataid2repoids.get(errata_id, []))

        for repo_id in available_repo_ids:
            if repo_id in errata_repo_ids:
                repo_ids.add(repo_id)

        return repo_ids

    def _build_nevra(self, update_pkg_id: int) -> str:
        name_id, evr_id, arch_id, _, _, _, _ = self.db_cache.package_details[update_pkg_id]
        name = self.db_cache.id2packagename[name_id]
        epoch, ver, rel = self.db_cache.id2evr[evr_id]
        arch = self.db_cache.id2arch[arch_id]
        nevra = join_rpm_name(name, epoch, ver, rel, arch)
        return nevra

    def _get_package_string(self, pkg_id: int, label_id: int) -> str:
        str_id = self.db_cache.package_details[pkg_id][label_id]
        result_str = self.db_cache.strings.get(str_id, None)
        return result_str

    def _get_pkg_errata_updates(self, update_pkg_id: int, errata_id: int, module_ids: set, available_repo_ids: set,
                                nevra: str, security_only: bool, third_party: bool,
                                current_pkg_from_module: bool) -> list:
        errata_name = self.db_cache.errataid2name[errata_id]
        errata_detail = self.db_cache.errata_detail[errata_name]

        # Filter out non-security updates
        if filter_non_security(errata_detail, security_only):
            return []

        # If we don't want third party content, and current advisory is third party, skip it
        if not third_party and errata_detail[ERRATA_THIRD_PARTY]:
            return []

        errata_modules = self.db_cache.pkgerrata2module.get((update_pkg_id, errata_id), set())
        if (errata_modules or current_pkg_from_module) and not errata_modules.intersection(module_ids):
            return []
        repo_ids = self._get_repositories(errata_id, available_repo_ids)
        pkg_errata_updates = []
        for repo_id in repo_ids:
            repo_details = self.db_cache.repo_detail[repo_id]
            pkg_errata_updates.append({
                'package': nevra,
                'erratum': errata_name,
                'repository': repo_details[REPO_LABEL],
                'basearch': none2empty(repo_details[REPO_BASEARCH]),
                'releasever': none2empty(repo_details[REPO_RELEASEVER])
            })
        return pkg_errata_updates

    def _get_pkg_updates(self, update_pkg_id: int, arch_id: int, security_only: bool, module_ids: set,
                         available_repo_ids: set, third_party: bool, current_pkg_from_module: bool) -> list:
        if arch_id is None:
            return []

        # Filter out packages without errata
        if update_pkg_id not in self.db_cache.pkgid2errataids:
            return []

        # Filter arch compatibility
        updated_nevra_arch_id = self.db_cache.package_details[update_pkg_id][2]
        if (updated_nevra_arch_id != arch_id
                and updated_nevra_arch_id not in self.db_cache.arch_compat[arch_id]):
            return []

        errata_ids = self.db_cache.pkgid2errataids.get(update_pkg_id, set())
        nevra = self._build_nevra(update_pkg_id)
        pkg_updates = []
        for errata_id in errata_ids:
            pkg_errata_updates = self._get_pkg_errata_updates(update_pkg_id, errata_id, module_ids, available_repo_ids,
                                                              nevra, security_only, third_party,
                                                              current_pkg_from_module)
            pkg_updates.extend(pkg_errata_updates)
        return pkg_updates

    def _get_optimistic_updates(self, name_id: int, pkg_dict: dict) -> list:
        _, epoch, ver, rel, _ = pkg_dict['parsed_nevra']
        updates = self.db_cache.updates[name_id]
        i = len(updates) - 1
        while i >= 0:
            # go from the end of list because we expect most system is up2date
            # therefore we will test just a few pkgs at the end
            update_pkg_id = updates[i]
            update_pkg = self.db_cache.package_details[update_pkg_id]
            update_evr_id = update_pkg[PKG_EVR_ID]
            update_epoch, update_ver, update_rel = self.db_cache.id2evr[update_evr_id]
            vercmp = rpm.labelCompare((str(update_epoch), update_ver, update_rel), (str(epoch), ver, rel))
            if vercmp <= 0:
                break
            i -= 1
        filtered_updates = updates[i + 1:]
        return filtered_updates

    def _append_metadata(self, pkg_data: dict, pkg_id: int, api_version: int) -> dict:
        if api_version == 1:
            pkg_data['summary'] = self._get_package_string(pkg_id, PKG_SUMMARY_ID)
            pkg_data['description'] = self._get_package_string(pkg_id, PKG_DESC_ID)
        return pkg_data

    def _is_pkg_from_enabled_module(self, pkg_id: int, module_ids: set, repo_ids: set) -> bool:
        errata = self.db_cache.pkgid2errataids.get(pkg_id, [])
        for eid in errata:
            erratum_repos = self.db_cache.errataid2repoids.get(eid, [])
            valid_repo = False
            for repo_id in repo_ids:
                if repo_id in erratum_repos:
                    valid_repo = True
                    break
            if not valid_repo:
                continue
            erratum_modules = self.db_cache.pkgerrata2module.get((pkg_id, eid), [])
            for erratum_module in erratum_modules:
                if erratum_module in module_ids:
                    return True
        return False

    def _get_nevra_updates(self, name_id: int, current_evr_ids: list, arch_id: int,
                           api_version: int, module_ids: set, available_repo_ids: set) -> (dict, list, bool):
        pkg_data = {'available_updates': []}
        current_nevra_pkg_id = self._get_nevra_pkg_id(name_id, current_evr_ids, arch_id)
        # Package with given NEVRA not found in cache/DB
        if not current_nevra_pkg_id:
            return pkg_data, [], False

        # append metadata according to API version
        pkg_data = self._append_metadata(pkg_data, current_nevra_pkg_id, api_version)

        current_from_module = self._is_pkg_from_enabled_module(current_nevra_pkg_id, module_ids, available_repo_ids)

        # No updates found for given NEVRA
        last_version_pkg_id = self.db_cache.updates[name_id][-1]
        if last_version_pkg_id == current_nevra_pkg_id:
            return pkg_data, [], current_from_module

        # Get candidate package IDs
        update_pkg_ids = self.db_cache.updates[name_id][current_evr_ids[-1] + 1:]
        return pkg_data, update_pkg_ids, current_from_module

    def _process_package_updates(self, api_version: int, pkg_dict: dict, available_repo_ids: set, module_ids: set,
                                 security_only: bool, third_party: bool) -> dict:
        name_id, current_evr_ids, arch_id = self._extract_nevra_ids(pkg_dict)
        update_pkg_ids = []
        pkg_from_module = False
        if current_evr_ids:
            pkg_data, update_pkg_ids, pkg_from_module = \
                self._get_nevra_updates(name_id, current_evr_ids, arch_id, api_version, module_ids, available_repo_ids)
        if not update_pkg_ids:
            # no nevra updates, try optimistic updates
            update_pkg_ids = self._get_optimistic_updates(name_id, pkg_dict)
            pkg_data = {'available_updates': []}
        if not update_pkg_ids:
            # still no updates, return empty UpdateDetail
            return {}

        # get repositories for update packages
        filtered_repo_ids = self._repos_by_pkgs(update_pkg_ids, available_repo_ids)

        if not pkg_data:
            pkg_data = {}
        for update_pkg_id in update_pkg_ids:
            pkg_updates = self._get_pkg_updates(update_pkg_id, arch_id, security_only, module_ids,
                                                filtered_repo_ids, third_party, pkg_from_module)
            pkg_data['available_updates'].extend(pkg_updates)
        return pkg_data

    def _process_updates(
            self,
            api_version: int,
            update_list: dict,
            packages: dict,
            repo_ids: set,
            module_ids: set,
            security_only: bool,
            third_party: bool
    ) -> dict:

        for pkg, pkg_dict in packages.items():
            update_list[pkg] = self._process_package_updates(api_version, pkg_dict, repo_ids, module_ids,
                                                             security_only, third_party)
        return update_list

    def _get_nevra_pkg_id(self, name_id: int, evr_indexes: list, arch_id: int) -> int:
        nevra_pkg_id = None
        for current_evr_index in evr_indexes:
            pkg_id = self.db_cache.updates[name_id][current_evr_index]
            nevra_arch_id = self.db_cache.package_details[pkg_id][2]
            if nevra_arch_id == arch_id:
                nevra_pkg_id = pkg_id
                break
        return nevra_pkg_id

    def _extract_nevra_ids(self, pkg_dict: dict) -> (int, list, int):
        name, epoch, ver, rel, arch = pkg_dict['parsed_nevra']
        name_id = self.db_cache.packagename2id[name]
        evr_id = self.db_cache.evr2id.get((epoch, ver, rel), None)
        arch_id = self.db_cache.arch2id.get(arch, None)
        current_evr_indexes = self.db_cache.updates_index[name_id].get(evr_id, [])
        return name_id, current_evr_indexes, arch_id

    def process_list(self, api_version: int, data: dict) -> dict:
        """
        This method is looking for updates of a package, including name of package to update to,
        associated erratum and repository this erratum is from.

        :param api_version: API version of the function
        :param data: input json, must contain package_list to find updates for them

        :returns: json with updates_list as a list of dictionaries
                  {'package': <p_name>, 'erratum': <e_name>, 'repository': <r_label>}
        """
        # Return empty update list in case of empty input package list
        packages_to_process, update_list = self.process_input_packages(data)
        response = {'update_list': update_list,
                    'last_change': format_datetime(self.db_cache.dbchange['last_change'])}
        if len(packages_to_process) == 0:
            return response

        repository_list, repo_ids = self._get_repository_list(data)
        response = insert_if_not_empty(response, 'repository_list', repository_list)

        repository_paths, repo_ids = self._get_repository_paths(data, repo_ids)
        response = insert_if_not_empty(response, 'repository_paths', repository_paths)

        releasever, repo_ids = self._get_releasever(data, repo_ids)
        response = insert_if_not_empty(response, 'releasever', releasever)

        # Get list of valid repository IDs based on input paramaters
        basearch, available_repo_ids = self._get_basearch(data, repo_ids)
        response = insert_if_not_empty(response, 'basearch', basearch)

        modules_list, module_ids = self._get_modules_list(data)
        response = insert_if_not_empty(response, 'modules_list', modules_list)

        # Backward compatibility of older APIs
        security_only = get_security_only(api_version, data)
        third_party = data.get('third_party', False)
        # Process updated packages, errata and fill the response
        update_list = self._process_updates(api_version, update_list, packages_to_process, available_repo_ids,
                                            module_ids, security_only, third_party)
        response['update_list'] = update_list
        return response
