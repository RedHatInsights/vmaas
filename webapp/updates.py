"""
Module to handle /updates API calls.
"""

from jsonschema import validate

from cache import REPO_LABEL, REPO_BASEARCH, REPO_RELEASEVER, REPO_PRODUCT_ID
from utils import join_packagename, split_packagename


JSON_SCHEMA = {
    'type' : 'object',
    'required': ['package_list'],
    'properties' : {
        'package_list': {
            'type': 'array', 'items': {'type': 'string'}, 'minItems' : 1
            },
        'repository_list': {
            'type': 'array', 'items': {'type' : 'string'}
            },
        'releasever' : {'type' : 'string'},
        'basearch' : {'type' : 'string'}
    }
}


class UpdatesAPI(object):
    """ Main /updates API class."""
    def __init__(self, cache):
        self.cache = cache

    def _process_repositories(self, data, response):
        # Read list of repositories
        repo_list = data.get('repository_list', None)
        if repo_list is not None:
            repo_ids = []
            for label in repo_list:
                repo_ids.extend(self.cache.repolabel2ids[label])
            response['repository_list'] = repo_list
        else:
            repo_ids = self.cache.repo_detail.keys()

        # Filter out repositories of different releasever
        releasever = data.get('releasever', None)
        if releasever is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.cache.repo_detail[oid][REPO_RELEASEVER] == releasever]
            response['releasever'] = releasever

        # Filter out repositories of different basearch
        basearch = data.get('basearch', None)
        if basearch is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.cache.repo_detail[oid][REPO_BASEARCH] == basearch]
            response['basearch'] = basearch

        return set(repo_ids)

    def _process_input_packages(self, data, response):
        """Parse input NEVRAs and filter out unknown (or without updates) package names."""
        packages_to_process = data.get('package_list', None)
        filtered_packages_to_process = {}
        if packages_to_process is not None:
            for pkg in packages_to_process:
                response['update_list'][pkg] = {}
                name, epoch, ver, rel, arch = split_packagename(pkg)
                if name in self.cache.packagename2id:
                    if self.cache.packagename2id[name] in self.cache.updates_index:
                        filtered_packages_to_process[pkg] = {'parsed_nevra': (name, epoch, ver, rel, arch)}
        return filtered_packages_to_process

    def _get_related_products(self, original_package_repo_ids):
        product_ids = set()
        for original_package_repo_id in original_package_repo_ids:
            product_ids.add(self.cache.repo_detail[original_package_repo_id][REPO_PRODUCT_ID])
        return product_ids

    def _get_valid_releasevers(self, original_package_repo_ids):
        valid_releasevers = set()
        for original_package_repo_id in original_package_repo_ids:
            valid_releasevers.add(self.cache.repo_detail[original_package_repo_id][REPO_RELEASEVER])
        return valid_releasevers

    def _get_repositories(self, product_ids, update_pkg_id, errata_ids, available_repo_ids, valid_releasevers):
        repo_ids = []
        errata_repo_ids = set()
        for errata_id in errata_ids:
            for repo_id in self.cache.errataid2repoids.get(errata_id, []):
                errata_repo_ids.add(repo_id)

        for repo_id in self.cache.pkgid2repoids.get(update_pkg_id, []):
            if repo_id in available_repo_ids \
                    and self.cache.repo_detail[repo_id][REPO_PRODUCT_ID] in product_ids \
                    and repo_id in errata_repo_ids \
                    and self.cache.repo_detail[repo_id][REPO_RELEASEVER] in valid_releasevers:
                repo_ids.append(repo_id)

        return repo_ids

    def _build_nevra(self, update_pkg_id):
        name_id, evr_id, arch_id, _, _ = self.cache.package_details[update_pkg_id]
        name = self.cache.id2packagename[name_id]
        epoch, ver, rel = self.cache.id2evr[evr_id]
        arch = self.cache.id2arch[arch_id]
        return join_packagename(name, epoch, ver, rel, arch)

    def _process_updates(self, packages_to_process, available_repo_ids, response):
        for pkg, pkg_dict in packages_to_process.items():
            name, epoch, ver, rel, arch = pkg_dict['parsed_nevra']
            name_id = self.cache.packagename2id[name]
            evr_id = self.cache.evr2id.get((epoch, ver, rel), None)
            arch_id = self.cache.arch2id.get(arch, None)
            current_evr_indexes = self.cache.updates_index[name_id].get(evr_id, [])

            # Package with given NEVRA not found in cache/DB
            if not current_evr_indexes:
                continue

            current_nevra_pkg_ids = set()
            for current_evr_index in current_evr_indexes:
                pkg_id = self.cache.updates[name_id][current_evr_index]
                current_nevra_arch_id = self.cache.package_details[pkg_id][2]
                if current_nevra_arch_id == arch_id:
                    current_nevra_pkg_ids.add(pkg_id)

            # Package with given NEVRA not found in cache/DB
            if not current_nevra_pkg_ids:
                continue

            pkg_id = next(iter(current_nevra_pkg_ids))
            response['update_list'][pkg]['summary'] = self.cache.package_details[pkg_id][3]
            response['update_list'][pkg]['description'] = self.cache.package_details[pkg_id][4]
            response['update_list'][pkg]['available_updates'] = []

            # No updates found for given NEVRA
            last_version_pkg_id = self.cache.updates[name_id][-1]
            if last_version_pkg_id in current_nevra_pkg_ids:
                continue

            # Get associated product IDs
            original_package_repo_ids = set()
            for current_nevra_pkg_id in current_nevra_pkg_ids:
                original_package_repo_ids.update(self.cache.pkgid2repoids.get(current_nevra_pkg_id, []))
            product_ids = self._get_related_products(original_package_repo_ids)
            valid_releasevers = self._get_valid_releasevers(original_package_repo_ids)

            # Get candidate package IDs
            update_pkg_ids = self.cache.updates[name_id][current_evr_indexes[-1] + 1:]

            for update_pkg_id in update_pkg_ids:
                # Filter out packages without errata
                if update_pkg_id not in self.cache.pkgid2errataids:
                    continue

                # Filter arch compatibility
                updated_nevra_arch_id = self.cache.package_details[update_pkg_id][2]
                if (updated_nevra_arch_id != arch_id
                        and updated_nevra_arch_id not in self.cache.arch_compat[arch_id]):
                    continue

                errata_ids = self.cache.pkgid2errataids.get(update_pkg_id, set())
                nevra = self._build_nevra(update_pkg_id)
                for errata_id in errata_ids:
                    repo_ids = self._get_repositories(product_ids, update_pkg_id, [errata_id], available_repo_ids,
                                                  valid_releasevers)
                    for repo_id in repo_ids:
                        repo_details = self.cache.repo_detail[repo_id]
                        response['update_list'][pkg]['available_updates'].append({
                            'package': nevra,
                            'erratum': self.cache.errataid2name[errata_id],
                            'repository': repo_details[REPO_LABEL],
                            'basearch': repo_details[REPO_BASEARCH],
                            'releasever': repo_details[REPO_RELEASEVER]
                        })

    def process_list(self, data):
        """
        This method is looking for updates of a package, including name of package to update to,
        associated erratum and repository this erratum is from.

        :param data: input json, must contain package_list to find updates for them

        :returns: json with updates_list as a list of dictionaries
                  {'package': <p_name>, 'erratum': <e_name>, 'repository': <r_label>}
        """
        validate(data, JSON_SCHEMA)

        response = {
            'update_list': {},
        }

        # Return empty update list in case of empty input package list
        packages_to_process = self._process_input_packages(data, response)

        if not packages_to_process:
            return response

        # Get list of valid repository IDs based on input paramaters
        available_repo_ids = self._process_repositories(data, response)

        # Process updated packages, errata and fill the response
        self._process_updates(packages_to_process, available_repo_ids, response)

        return response
