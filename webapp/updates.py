"""
Module to handle /updates API calls.
"""

from cache import REPO_LABEL, REPO_BASEARCH, REPO_RELEASEVER, REPO_URL, PKG_SUMMARY_ID, PKG_DESC_ID, PKG_EVR_ID, \
    ERRATA_CVE, ERRATA_TYPE
from common.webapp_utils import none2empty, filter_package_list
from common.rpm import parse_rpm_name, join_rpm_name

SECURITY_ERRATA_TYPE = 'security'


class UpdatesAPI:
    """ Main /updates API class."""
    def __init__(self, db_cache):
        self.db_cache = db_cache      # DB dump in memory, stored like a dict

    def _process_repositories(self, data, response):
        # Read list of repositories
        repo_list = data.get('repository_list', None)
        if repo_list is not None:
            repo_ids = []
            for label in repo_list:
                repo_id = self.db_cache.repolabel2ids.get(label, None)
                if repo_id:
                    repo_ids.extend(repo_id)
            response['repository_list'] = repo_list
        else:
            repo_ids = self.db_cache.repo_detail.keys()

        # Filter out repositories of different releasever
        releasever = data.get('releasever', None)
        if releasever is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.db_cache.repo_detail[oid][REPO_RELEASEVER] == releasever
                        or (self.db_cache.repo_detail[oid][REPO_RELEASEVER] is None
                            and releasever in self.db_cache.repo_detail[oid][REPO_URL])]
            response['releasever'] = releasever

        # Filter out repositories of different basearch
        basearch = data.get('basearch', None)
        if basearch is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.db_cache.repo_detail[oid][REPO_BASEARCH] == basearch
                        or (self.db_cache.repo_detail[oid][REPO_BASEARCH] is None
                            and basearch in self.db_cache.repo_detail[oid][REPO_URL])]
            response['basearch'] = basearch

        return set(repo_ids)

    def _process_input_packages(self, data, response):
        """Parse input NEVRAs and filter out unknown (or without updates) package names."""
        latest_only = data.get("latest_only", False)
        packages_to_process = filter_package_list(data.get('package_list', None), latest_only)
        filtered_packages_to_process = {}
        if packages_to_process is not None:
            for pkg in packages_to_process:
                response['update_list'][pkg] = {}
                name, epoch, ver, rel, arch = parse_rpm_name(pkg, default_epoch='0')
                if name in self.db_cache.packagename2id:
                    if self.db_cache.packagename2id[name] in self.db_cache.updates_index:
                        filtered_packages_to_process[pkg] = {'parsed_nevra': (name, epoch, ver, rel, arch)}
        return filtered_packages_to_process

    def _get_valid_releasevers(self, original_package_repo_ids):
        valid_releasevers = set()
        for original_package_repo_id in original_package_repo_ids:
            valid_releasevers.add(self.db_cache.repo_detail[original_package_repo_id][REPO_RELEASEVER])
        return valid_releasevers

    def _get_repositories(self, update_pkg_id, errata_ids, available_repo_ids, valid_releasevers):
        repo_ids = set()
        errata_repo_ids = set()
        for errata_id in errata_ids:
            errata_repo_ids.update(self.db_cache.errataid2repoids.get(errata_id, []))

        res_repos = set(self.db_cache.pkgid2repoids.get(update_pkg_id, []))
        res_repos.intersection_update(available_repo_ids, errata_repo_ids)

        for repo_id in res_repos:
            repo_detail = self.db_cache.repo_detail[repo_id]
            if repo_detail[REPO_RELEASEVER] in valid_releasevers:
                repo_ids.add(repo_id)

        return repo_ids

    def _build_nevra(self, update_pkg_id):
        name_id, evr_id, arch_id, _, _, _ = self.db_cache.package_details[update_pkg_id]
        name = self.db_cache.id2packagename[name_id]
        epoch, ver, rel = self.db_cache.id2evr[evr_id]
        arch = self.db_cache.id2arch[arch_id]
        return join_rpm_name(name, epoch, ver, rel, arch)

    def _process_updates(self, packages_to_process, api_version, available_repo_ids,
                         response, module_ids, security_only, optimistic_updates):
        # pylint: disable=too-many-branches
        for pkg, pkg_dict in packages_to_process.items():
            name, epoch, ver, rel, arch = pkg_dict['parsed_nevra']
            name_id = self.db_cache.packagename2id[name]
            evr_id = self.db_cache.evr2id.get((epoch, ver, rel), None)
            arch_id = self.db_cache.arch2id.get(arch, None)
            current_evr_indexes = []

            if evr_id is not None:
                current_evr_indexes = self.db_cache.updates_index[name_id].get(evr_id, [])
            elif optimistic_updates:
                # Try to find an evra, which can be used as an anchor point
                for idx, pkg_id in enumerate(self.db_cache.updates[name_id]):
                    evr = self.db_cache.id2evr.get(self.db_cache.package_details[PKG_EVR_ID], None)
                    if evr > (epoch, ver, rel):
                        current_evr_indexes = list(range(idx, len(self.db_cache.updates[name_id])))

            # Package with given NEVRA not found in cache/DB
            if not current_evr_indexes:
                continue

            current_nevra_pkg_id = None
            for current_evr_index in current_evr_indexes:
                pkg_id = self.db_cache.updates[name_id][current_evr_index]
                current_nevra_arch_id = self.db_cache.package_details[pkg_id][2]
                if current_nevra_arch_id == arch_id:
                    current_nevra_pkg_id = pkg_id
                    break

            # Package with given NEVRA not found in cache/DB
            if not current_nevra_pkg_id:
                continue

            if api_version == 1:
                sum_id = self.db_cache.package_details[current_nevra_pkg_id][PKG_SUMMARY_ID]
                response['update_list'][pkg]['summary'] = self.db_cache.strings.get(sum_id, None)

                desc_id = self.db_cache.package_details[current_nevra_pkg_id][PKG_DESC_ID]
                response['update_list'][pkg]['description'] = self.db_cache.strings.get(desc_id, None)

            response['update_list'][pkg]['available_updates'] = []

            # No updates found for given NEVRA
            last_version_pkg_id = self.db_cache.updates[name_id][-1]
            if last_version_pkg_id == current_nevra_pkg_id:
                continue

            # Get associated product IDs
            original_package_repo_ids = set()
            original_package_repo_ids.update(self.db_cache.pkgid2repoids.get(current_nevra_pkg_id, []))
            valid_releasevers = self._get_valid_releasevers(original_package_repo_ids)

            # Get candidate package IDs
            update_pkg_ids = self.db_cache.updates[name_id][current_evr_indexes[-1] + 1:]

            for update_pkg_id in update_pkg_ids:
                # Filter out packages without errata
                if update_pkg_id not in self.db_cache.pkgid2errataids:
                    continue

                # Filter arch compatibility
                updated_nevra_arch_id = self.db_cache.package_details[update_pkg_id][2]
                if (updated_nevra_arch_id != arch_id
                        and updated_nevra_arch_id not in self.db_cache.arch_compat[arch_id]):
                    continue

                errata_ids = self.db_cache.pkgid2errataids.get(update_pkg_id, set())
                nevra = self._build_nevra(update_pkg_id)
                for errata_id in errata_ids:
                    errata_name = self.db_cache.errataid2name[errata_id]
                    # Filter out non-security updates
                    if security_only and not (
                            self.db_cache.errata_detail[errata_name][ERRATA_TYPE] == SECURITY_ERRATA_TYPE or \
                            self.db_cache.errata_detail[errata_name][ERRATA_CVE]):
                        continue
                    if ((update_pkg_id, errata_id) in self.db_cache.pkgerrata2module and not \
                            self.db_cache.pkgerrata2module[(update_pkg_id, errata_id)].intersection(module_ids)):
                        continue
                    repo_ids = self._get_repositories(update_pkg_id, [errata_id], available_repo_ids,
                                                      valid_releasevers)
                    for repo_id in repo_ids:
                        repo_details = self.db_cache.repo_detail[repo_id]
                        response['update_list'][pkg]['available_updates'].append({
                            'package': nevra,
                            'erratum': errata_name,
                            'repository': repo_details[REPO_LABEL],
                            'basearch': none2empty(repo_details[REPO_BASEARCH]),
                            'releasever': none2empty(repo_details[REPO_RELEASEVER])
                        })

    def process_list(self, api_version, data):
        """
        This method is looking for updates of a package, including name of package to update to,
        associated erratum and repository this erratum is from.

        :param data: input json, must contain package_list to find updates for them

        :returns: json with updates_list as a list of dictionaries
                  {'package': <p_name>, 'erratum': <e_name>, 'repository': <r_label>}
        """
        # pylint: disable=too-many-branches
        response = {
            'update_list': {},
        }

        # Get list of valid repository IDs based on input paramaters
        available_repo_ids = self._process_repositories(data, response)
        modules_list = data.get('modules_list', [])
        module_info = [(x['module_name'], x['module_stream']) for x in modules_list]
        module_ids = set()
        for module in module_info:
            if module in self.db_cache.modulename2id:
                module_ids.update(self.db_cache.modulename2id[module])
        if 'modules_list' in data:
            response['modules_list'] = modules_list

        # Backward compatibility of older APIs
        if api_version < 3:
            security_only = True
        else:
            security_only = data.get("security_only", False)

        optimistic_updates = data.get("optimistic_updates", False)

        # Return empty update list in case of empty input package list
        packages_to_process = self._process_input_packages(data, response)

        if not packages_to_process:
            return response

        # Process updated packages, errata and fill the response
        self._process_updates(packages_to_process, api_version,
                              available_repo_ids, response, module_ids,
                              security_only, optimistic_updates)

        return response
