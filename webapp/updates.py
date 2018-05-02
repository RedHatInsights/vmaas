"""
Module to handle /updates API calls.
"""

from jsonschema import validate

from database import NamedCursor
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


class UpdatesCache(object):
    """Cache which hold updates mappings."""
    # pylint: disable=too-few-public-methods, too-many-instance-attributes, too-many-locals
    def __init__(self, db_instance):
        self.db_instance = db_instance
        self.packagename2id = {}
        self.id2packagename = {}
        self.updates = {}
        self.updates_index = {}
        self.evr2id = {}
        self.id2evr = {}
        self.arch2id = {}
        self.id2arch = {}
        self.arch_compat = {}
        self.package_details = {}
        self.pkgid2repoids = {}
        self.errataid2name = {}
        self.pkgid2errataids = {}
        self.errataid2repoids = {}
        self.prepare()

    def prepare(self):
        """ Read ahead table of keys. """

        # Select all package names (only for package names with ever received sec. update)
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("""select distinct pn.id, pn.name
                              from package_name pn inner join
                                   package p on pn.id = p.name_id inner join
                                   pkg_errata pe on p.id = pe.pkg_id inner join
                                   errata e on pe.errata_id = e.id inner join
                                   errata_type et on e.errata_type_id = et.id left join
                                   errata_cve ec on e.id = ec.errata_id
                              where et.name = 'security' or ec.cve_id is not null
                           """)
            for name_id, pkg_name in cursor:
                self.packagename2id[pkg_name] = name_id
                self.id2packagename[name_id] = pkg_name

        # Select ordered updates lists for previously selected package names
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("""select p.name_id, p.id, p.evr_id, p.arch_id
                              from package p inner join 
                                   evr on p.evr_id = evr.id
                              where p.name_id in %s
                              order by p.name_id, evr.evr
                           """, [tuple(self.packagename2id.values())])
            index_cnt = {}
            for name_id, pkg_id, evr_id, arch_id in cursor:
                idx = index_cnt.get(name_id, 0)
                self.updates.setdefault(name_id, []).append(pkg_id)
                self.updates_index.setdefault(name_id, {}).setdefault((evr_id, arch_id), []).append(idx)
                idx += 1
                index_cnt[name_id] = idx

        # Select all evrs and put them into dictionary
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("select id, epoch, version, release from evr")
            for evr_id, epoch, ver, rel in cursor:
                self.evr2id[(epoch, ver, rel)] = evr_id
                self.id2evr[evr_id] = (epoch, ver, rel)

        # Select all archs and put them into dictionary
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("select id, name from arch")
            for arch_id, name in cursor:
                self.arch2id[name] = arch_id
                self.id2arch[arch_id] = name

        # Select information about archs compatibility
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("select from_arch_id, to_arch_id from arch_compatibility")
            for from_arch_id, to_arch_id in cursor:
                self.arch_compat.setdefault(from_arch_id, set()).add(to_arch_id)

        # Select details about packages (for previously selected package names)
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("""select id, name_id, evr_id, arch_id, summary, description
                              from package
                              where name_id in %s
                           """, [tuple(self.packagename2id.values())])
            for pkg_id, name_id, evr_id, arch_id, summary, description in cursor:
                self.package_details[pkg_id] = (name_id, evr_id, arch_id, summary, description)

        # Select package ID to repo IDs mapping
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("""select pkg_id, repo_id
                              from pkg_repo
                              where pkg_id in %s
                           """, [tuple(self.package_details.keys())])
            for pkg_id, repo_id in cursor:
                self.pkgid2repoids.setdefault(pkg_id, []).append(repo_id)

        # Select errata ID to name mapping
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("""select distinct e.id, e.name
                              from errata e inner join
                                   errata_type et on e.errata_type_id = et.id left join
                                   errata_cve ec on e.id = ec.errata_id
                              where et.name = 'security' or ec.cve_id is not null
                           """)
            for errata_id, errata_name in cursor:
                self.errataid2name[errata_id] = errata_name

        # Select package ID to errata IDs mapping, only for relevant errata
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("""select pkg_id, errata_id
                              from pkg_errata
                              where errata_id in %s
                           """, [tuple(self.errataid2name.keys())])
            for pkg_id, errata_id in cursor:
                self.pkgid2errataids.setdefault(pkg_id, set()).add(errata_id)

        # Select errata ID to repo IDs mapping, only for relevant errata
        with NamedCursor(self.db_instance, name="updates-cache") as cursor:
            cursor.execute("""select errata_id, repo_id
                              from errata_repo
                              where errata_id in %s
                           """, [tuple(self.errataid2name.keys())])
            for errata_id, repo_id in cursor:
                self.errataid2repoids.setdefault(errata_id, set()).add(repo_id)


class UpdatesAPI(object):
    """ Main /updates API class."""
    # pylint: disable=too-few-public-methods
    def __init__(self, updatescache, repocache):
        self.updatescache = updatescache
        self.repocache = repocache

    def _process_repositories(self, data, response):
        # Read list of repositories
        repo_list = data.get('repository_list', None)
        if repo_list is not None:
            repo_ids = []
            for label in repo_list:
                repo_ids.extend(self.repocache.label2ids(label))
            response['repository_list'] = repo_list
        else:
            repo_ids = self.repocache.all_ids()

        # Filter out repositories of different releasever
        releasever = data.get('releasever', None)
        if releasever is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.repocache.get_by_id(oid)['releasever'] == releasever]
            response['releasever'] = releasever

        # Filter out repositories of different basearch
        basearch = data.get('basearch', None)
        if basearch is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.repocache.get_by_id(oid)['basearch'] == basearch]
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
                if name in self.updatescache.packagename2id:
                    if self.updatescache.packagename2id[name] in self.updatescache.updates_index:
                        filtered_packages_to_process[pkg] = {'parsed_nevra': (name, epoch, ver, rel, arch)}
        return filtered_packages_to_process

    def _get_related_products(self, original_package_repo_ids):
        product_ids = set()
        for original_package_repo_id in original_package_repo_ids:
            product_ids.add(self.repocache.id2productid(original_package_repo_id))
        return product_ids

    def _get_valid_releasevers(self, original_package_repo_ids):
        valid_releasevers = set()
        for original_package_repo_id in original_package_repo_ids:
            valid_releasevers.add(self.repocache.get_by_id(original_package_repo_id)['releasever'])
        return valid_releasevers

    # pylint: disable=too-many-arguments
    def _get_repositories(self, product_ids, update_pkg_id, errata_ids, available_repo_ids, valid_releasevers):
        repo_ids = []
        errata_repo_ids = set()
        for errata_id in errata_ids:
            for repo_id in self.updatescache.errataid2repoids[errata_id]:
                errata_repo_ids.add(repo_id)

        for repo_id in self.updatescache.pkgid2repoids[update_pkg_id]:
            if repo_id in available_repo_ids \
                    and self.repocache.id2productid(repo_id) in product_ids \
                    and repo_id in errata_repo_ids \
                    and self.repocache.get_by_id(repo_id)['releasever'] in valid_releasevers:
                repo_ids.append(repo_id)

        return repo_ids

    def _build_nevra(self, update_pkg_id):
        name_id, evr_id, arch_id, _, _ = self.updatescache.package_details[update_pkg_id]
        name = self.updatescache.id2packagename[name_id]
        epoch, ver, rel = self.updatescache.id2evr[evr_id]
        arch = self.updatescache.id2arch[arch_id]
        return join_packagename(name, epoch, ver, rel, arch)

    def _process_updates(self, packages_to_process, available_repo_ids, response):
        # pylint: disable=too-many-locals
        for pkg, pkg_dict in packages_to_process.items():
            name, epoch, ver, rel, arch = pkg_dict['parsed_nevra']
            name_id = self.updatescache.packagename2id[name]
            evr_id = self.updatescache.evr2id.get((epoch, ver, rel), None)
            arch_id = self.updatescache.arch2id.get(arch, None)
            current_version_indexes = self.updatescache.updates_index[name_id].get((evr_id, arch_id), [])

            # Package with given NEVRA not found in cache/DB
            if not current_version_indexes:
                continue

            current_version_pkg_ids = set()
            pkg_id = None
            for current_version_index in current_version_indexes:
                pkg_id = self.updatescache.updates[name_id][current_version_index]
                current_version_pkg_ids.add(pkg_id)

            _, _, current_version_arch_id, summary, description = \
                self.updatescache.package_details[pkg_id]
            response['update_list'][pkg]['summary'] = summary
            response['update_list'][pkg]['description'] = description
            response['update_list'][pkg]['available_updates'] = []

            # No updates found for given NEVRA
            last_version_pkg_id = self.updatescache.updates[name_id][-1]
            if last_version_pkg_id in current_version_pkg_ids:
                continue

            # Get associated product IDs
            original_package_repo_ids = set()
            for current_version_pkg_id in current_version_pkg_ids:
                original_package_repo_ids.update(self.updatescache.pkgid2repoids[current_version_pkg_id])
            product_ids = self._get_related_products(original_package_repo_ids)
            valid_releasevers = self._get_valid_releasevers(original_package_repo_ids)

            # Get candidate package IDs
            update_pkg_ids = self.updatescache.updates[name_id][current_version_indexes[-1] + 1:]

            for update_pkg_id in update_pkg_ids:
                # Filter out packages without errata
                if update_pkg_id not in self.updatescache.pkgid2errataids:
                    continue

                # Filter arch compatibility
                _, _, updated_version_arch_id, _, _ = self.updatescache.package_details[update_pkg_id]
                if (updated_version_arch_id != current_version_arch_id
                        and updated_version_arch_id not in self.updatescache.arch_compat[current_version_arch_id]):
                    continue

                errata_ids = self.updatescache.pkgid2errataids.get(update_pkg_id, set())
                repo_ids = self._get_repositories(product_ids, update_pkg_id, errata_ids, available_repo_ids,
                                                  valid_releasevers)
                nevra = self._build_nevra(update_pkg_id)
                for repo_id in repo_ids:
                    repo_details = self.repocache.get_by_id(repo_id)
                    for errata_id in errata_ids:
                        response['update_list'][pkg]['available_updates'].append({
                            'package': nevra,
                            'erratum': self.updatescache.errataid2name[errata_id],
                            'repository': repo_details['label'],
                            'basearch': repo_details['basearch'],
                            'releasever': repo_details['releasever']
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
