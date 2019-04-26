"""
Module to handle /updates API calls.
"""

import os
import hashlib
from jsonschema import validate

from probes import HOT_CACHE_INSERTS, HOT_CACHE_REMOVAL, UPDATES_CACHE_HITS, UPDATES_CACHE_MISSES
from cache import REPO_LABEL, REPO_BASEARCH, REPO_RELEASEVER, REPO_PRODUCT_ID, REPO_URL
from utils import join_packagename, split_packagename, none2empty


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
        'modules_list': {
            'type': 'array',
            'items': {
                'type': 'object',
                'required': ['module_name', 'module_stream'],
                'properties': {
                    'module_name': {'type': 'string'},
                    'module_stream': {'type': 'string'}
                }
            }
        },
        'releasever' : {'type' : 'string'},
        'basearch' : {'type' : 'string'}
    }
}


class CacheNode:
    """Node of a binary tree"""

    def __init__(self, key, cached_response=None):
        self.key = key
        self.cached_response = cached_response
        self.left = self.right = None


class HotCache:
    """Splay Tree implementaion, see https://en.wikipedia.org/wiki/Splay_tree for the details

        We use this tree to store cached data in nodes,
        as a key we use NEVRA of a package as a data - cached response with updates
        There is no delete node method, instead of this there is pruning() method, which
        works as a primitive 'stop-the-world' Garbage Collector.
        Every 'max_inserts_per_pruning' the cache runs pruning() and removes all the nodes which
        lie lower than 'max cache level'. So the total number of nodes depends on balance factor.
        For the total unbalanced tree (linked-list in other words), we have only
        'max_cache_levels' nodes. On the other hand, a complete binary tree can contain
        2^max_cache_levels * 2 - 1 nodes.
    """

    def __init__(self):
        self.root = None
        self.header = CacheNode(None)  # workaround, need for the splay()
        self.inserts = 0
        self.max_inserts_per_pruning = int(os.getenv("HOTCACHE_PRUNING", "1024"))
        self.max_cache_levels = int(os.getenv("HOTCACHE_LEVELS", "11"))

    def insert(self, key, cached_response):
        """
        Insert new node or update an existing.
        :param key: NEVRA of a package
        :param cached_response: dictionary with updates
        :return:
        """

        if self.root is None:
            self.root = CacheNode(key, cached_response)
            self.inserts = 1
            return

        self._splay(key)

        if self.root.key == key:
            # update only, we already have this key in the tree
            self.root.cached_response = cached_response
            return

        new_node = CacheNode(key, cached_response)

        if key < self.root.key:
            new_node.left = self.root.left
            new_node.right = self.root
            self.root.left = None
        else:
            new_node.right = self.root.right
            new_node.left = self.root
            self.root.right = None
        self.root = new_node

        self.inserts += 1
        if self.inserts > self.max_inserts_per_pruning:
            self._pruning(self.root, 1)
            self.inserts = 0

    def find(self, key):
        """
        Find a node.
        :param key: key of node
        :return:  CacheNode object or None if node with this key doesn't exist
        """

        if self.root is None:
            return None
        self._splay(key)
        if self.root.key != key:
            return None
        return self.root.cached_response

    def _splay(self, key):
        """
        Perform splaying operations - Zig, Zig-Zig or Zig-Zag
        rotations
        :param key:
        :return:
        """
        left = right = self.header
        cur = self.root
        self.header.left = self.header.right = None
        while True:
            if key < cur.key:
                if cur.left is None:
                    break
                if key < cur.left.key:
                    tmp = cur.left
                    cur.left = tmp.right
                    tmp.right = cur
                    cur = tmp
                    if cur.left is None:
                        break
                right.left = cur
                right = cur
                cur = cur.left
            elif key > cur.key:
                if cur.right is None:
                    break
                if key > cur.right.key:
                    tmp = cur.right
                    cur.right = tmp.left
                    tmp.left = cur
                    cur = tmp
                    if cur.right is None:
                        break
                left.right = cur
                left = cur
                cur = cur.right
            else:
                break
        left.right = cur.left
        right.left = cur.right
        cur.left = self.header.right
        cur.right = self.header.left
        self.root = cur

    def _pruning(self, node, level):
        """
        Recursively remove all nodes from the tree which lie lower than self.max_cache_levels
        :param node: current processing node
        :param level: current cache level
        :return:
        """
        if level == self.max_cache_levels:
            HOT_CACHE_REMOVAL.inc()
            node.left = None
            node.right = None
            return

        # pruning left child
        if node.left is not None:
            self._pruning(node.left, level=level + 1)

        # pruning right child
        if node.right is not None:
            self._pruning(node.right, level=level + 1)


class UpdatesAPI:
    """ Main /updates API class."""
    def __init__(self, db_cache):
        self.db_cache = db_cache      # DB dump in memory, stored like a dict
        self.hot_cache = HotCache()   # hot cache of the application, splay tree
        self.use_hot_cache = "YES"

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
        packages_to_process = data.get('package_list', None)
        filtered_packages_to_process = {}
        if packages_to_process is not None:
            for pkg in packages_to_process:
                response['update_list'][pkg] = {}
                name, epoch, ver, rel, arch = split_packagename(pkg)
                if name in self.db_cache.packagename2id:
                    if self.db_cache.packagename2id[name] in self.db_cache.updates_index:
                        filtered_packages_to_process[pkg] = {'parsed_nevra': (name, epoch, ver, rel, arch)}
        return filtered_packages_to_process

    def _get_related_products(self, original_package_repo_ids):
        product_ids = set()
        for original_package_repo_id in original_package_repo_ids:
            product_ids.add(self.db_cache.repo_detail[original_package_repo_id][REPO_PRODUCT_ID])
        return product_ids

    def _get_valid_releasevers(self, original_package_repo_ids):
        valid_releasevers = set()
        for original_package_repo_id in original_package_repo_ids:
            valid_releasevers.add(self.db_cache.repo_detail[original_package_repo_id][REPO_RELEASEVER])
        return valid_releasevers

    def _get_repositories(self, product_ids, update_pkg_id, errata_ids, available_repo_ids, valid_releasevers):
        repo_ids = []
        errata_repo_ids = set()
        for errata_id in errata_ids:
            for repo_id in self.db_cache.errataid2repoids.get(errata_id, []):
                errata_repo_ids.add(repo_id)

        for repo_id in self.db_cache.pkgid2repoids.get(update_pkg_id, []):
            if repo_id in available_repo_ids \
                    and self.db_cache.repo_detail[repo_id][REPO_PRODUCT_ID] in product_ids \
                    and repo_id in errata_repo_ids \
                    and self.db_cache.repo_detail[repo_id][REPO_RELEASEVER] in valid_releasevers:
                repo_ids.append(repo_id)

        return repo_ids

    def _build_nevra(self, update_pkg_id):
        name_id, evr_id, arch_id, _, _ = self.db_cache.package_details[update_pkg_id]
        name = self.db_cache.id2packagename[name_id]
        epoch, ver, rel = self.db_cache.id2evr[evr_id]
        arch = self.db_cache.id2arch[arch_id]
        return join_packagename(name, epoch, ver, rel, arch)

    def _process_updates(self, packages_to_process, api_version, available_repo_ids,
                         repo_ids_key, response, module_ids):
        # pylint: disable=too-many-branches
        module_filter = module_ids is not None
        for pkg, pkg_dict in packages_to_process.items():
            name, epoch, ver, rel, arch = pkg_dict['parsed_nevra']
            name_id = self.db_cache.packagename2id[name]
            evr_id = self.db_cache.evr2id.get((epoch, ver, rel), None)
            arch_id = self.db_cache.arch2id.get(arch, None)
            current_evr_indexes = self.db_cache.updates_index[name_id].get(evr_id, [])

            # Package with given NEVRA not found in cache/DB
            if not current_evr_indexes:
                continue

            current_nevra_pkg_ids = set()
            for current_evr_index in current_evr_indexes:
                pkg_id = self.db_cache.updates[name_id][current_evr_index]
                current_nevra_arch_id = self.db_cache.package_details[pkg_id][2]
                if current_nevra_arch_id == arch_id:
                    current_nevra_pkg_ids.add(pkg_id)

            # Package with given NEVRA not found in cache/DB
            if not current_nevra_pkg_ids:
                continue

            pkg_id = next(iter(current_nevra_pkg_ids))
            if api_version == 1:
                response['update_list'][pkg]['summary'] = self.db_cache.package_details[pkg_id][3]
                response['update_list'][pkg]['description'] = self.db_cache.package_details[pkg_id][4]
            response['update_list'][pkg]['available_updates'] = []

            # No updates found for given NEVRA
            last_version_pkg_id = self.db_cache.updates[name_id][-1]
            if last_version_pkg_id in current_nevra_pkg_ids:
                continue

            # Get associated product IDs
            original_package_repo_ids = set()
            for current_nevra_pkg_id in current_nevra_pkg_ids:
                original_package_repo_ids.update(self.db_cache.pkgid2repoids.get(current_nevra_pkg_id, []))
            product_ids = self._get_related_products(original_package_repo_ids)
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
                    if (module_filter and (update_pkg_id, errata_id) in self.db_cache.pkgerrata2module and not
                            self.db_cache.pkgerrata2module[(update_pkg_id, errata_id)].intersection(module_ids)):
                        continue
                    repo_ids = self._get_repositories(product_ids, update_pkg_id, [errata_id], available_repo_ids,
                                                      valid_releasevers)
                    for repo_id in repo_ids:
                        repo_details = self.db_cache.repo_detail[repo_id]
                        response['update_list'][pkg]['available_updates'].append({
                            'package': nevra,
                            'erratum': self.db_cache.errataid2name[errata_id],
                            'repository': repo_details[REPO_LABEL],
                            'basearch': none2empty(repo_details[REPO_BASEARCH]),
                            'releasever': none2empty(repo_details[REPO_RELEASEVER])
                        })

            if self.use_hot_cache.upper() == "YES":
                HOT_CACHE_INSERTS.inc()
                self.hot_cache.insert(repo_ids_key + pkg, response['update_list'][pkg])

    def clear_hot_cache(self):
        """
        This method clears HotCache
        """

        self.hot_cache = HotCache()

    def process_list(self, api_version, data):
        """
        This method is looking for updates of a package, including name of package to update to,
        associated erratum and repository this erratum is from.

        :param data: input json, must contain package_list to find updates for them

        :returns: json with updates_list as a list of dictionaries
                  {'package': <p_name>, 'erratum': <e_name>, 'repository': <r_label>}
        """
        # pylint: disable=too-many-branches
        validate(data, JSON_SCHEMA)

        response = {
            'update_list': {},
        }

        # Get list of valid repository IDs based on input paramaters
        available_repo_ids = self._process_repositories(data, response)
        modules_list = data.get('modules_list', None)
        if modules_list is not None:
            module_info = [(x['module_name'], x['module_stream']) for x in modules_list]
            module_ids = set()
            for module in module_info:
                if module in self.db_cache.modulename2id:
                    module_ids.update(self.db_cache.modulename2id[module])
            response['modules_list'] = modules_list
        else:
            module_ids = None

        hashlib_elements = []
        hashlib_elements.append(str(api_version))
        hashlib_elements.extend([str(r_id) for r_id in sorted(available_repo_ids)])
        if module_ids is not None:
            if module_ids:
                hashlib_elements.extend([str(m_id) for m_id in sorted(module_ids)])
            else:
                hashlib_elements.extend('no_enabled_modules')
        repo_ids_key = hashlib.md5('_'.join(hashlib_elements).encode('utf-8')).hexdigest()

        all_pkgs = data.get('package_list', None)
        pkgs_not_in_cache = []
        self.use_hot_cache = os.getenv("HOTCACHE_ENABLED", "YES")

        if all_pkgs is not None:
            for name in all_pkgs:
                if self.use_hot_cache.upper() == "YES":
                    resp = self.hot_cache.find(repo_ids_key + name)

                    if resp is not None:
                        UPDATES_CACHE_HITS.inc()
                        response['update_list'][name] = resp
                    else:
                        UPDATES_CACHE_MISSES.inc()
                        pkgs_not_in_cache.append(name)
                else:
                    # no need to put counter here as caching is disabled
                    pkgs_not_in_cache.append(name)

        # Start main processing of packages which are not in the hot cache
        data['package_list'] = pkgs_not_in_cache

        # Return empty update list in case of empty input package list
        packages_to_process = self._process_input_packages(data, response)

        if not packages_to_process:
            return response

        # Process updated packages, errata and fill the response
        self._process_updates(packages_to_process, api_version,
                              available_repo_ids, repo_ids_key, response, module_ids)

        return response
