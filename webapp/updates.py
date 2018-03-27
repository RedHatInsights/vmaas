"""
Module to handle /updates API calls.
"""

from utils import join_packagename, split_packagename


class UpdatesAPI(object):
    """ Main /updates API class. """
    def __init__(self, cursor, repocache):
        self.cursor = cursor
        self.repocache = repocache
        self.evr2id_dict = {}
        self.id2evr_dict = {}
        self.arch2id_dict = {}
        self.id2arch_dict = {}

        self.prepare()

    def prepare(self):
        """ Read ahead table of keys. """
        # Select all evrs and put them into dictionary
        self.cursor.execute("SELECT id, epoch, version, release from evr")
        evrs = self.cursor.fetchall()
        for evr_id, evr_epoch, evr_ver, evr_rel in evrs:
            key = "%s:%s:%s" % (evr_epoch, evr_ver, evr_rel)
            self.evr2id_dict[key] = evr_id
            self.id2evr_dict[evr_id] = {'epoch': evr_epoch, 'version': evr_ver, 'release': evr_rel}

        # Select all archs and put them into dictionary
        self.cursor.execute("SELECT id, name from arch")
        archs = self.cursor.fetchall()
        for arch_id, arch_name in archs:
            self.arch2id_dict[arch_name] = arch_id
            self.id2arch_dict[arch_id] = arch_name


    def process_list(self, data):
        #pylint: disable=too-many-locals,too-many-statements,too-many-branches
        """
        This method is looking for updates of a package, including name of package to update to,
        associated erratum and repository this erratum is from.

        :param data: input json, must contain package_list to find updates for them

        :returns: json with updates_list as a list of dictionaries
                  {'package': <p_name>, 'erratum': <e_name>, 'repository': <r_label>}
        """
        packages_to_process = data['package_list']
        response = {
            'update_list': {},
        }
        auxiliary_dict = {}
        answer = {}

        if not packages_to_process:
            return response

        # Read list of repositories
        repo_ids = None
        provided_repo_labels = None
        if 'repository_list' in data:
            provided_repo_labels = data['repository_list']

            if provided_repo_labels:
                repo_ids = []
                for label in provided_repo_labels:
                    repo_ids.extend(self.repocache.label2ids(label))
        else:
            repo_ids = self.repocache.all_ids()

        # Filter out repositories of different releasever
        releasever = data.get('releasever', None)
        if releasever is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.repocache.get_by_id(oid)['releasever'] == releasever]

        # Filter out repositories of different basearch
        basearch = data.get('basearch', None)
        if basearch is not None:
            repo_ids = [oid for oid in repo_ids
                        if self.repocache.get_by_id(oid)['basearch'] == basearch]

        # Parse input list of packages and create empty update list (answer) for them
        packages_names = []
        packages_evrids = []
        for pkg in packages_to_process:
            pkg = str(pkg)

            # process all packages form input
            if pkg not in auxiliary_dict:
                pkg_name, pkg_epoch, pkg_ver, pkg_rel, pkg_arch = split_packagename(str(pkg))
                auxiliary_dict[pkg] = {}  # fill auxiliary dictionary with empty data for every package
                answer[pkg] = []          # fill answer with empty data

                evr_key = "%s:%s:%s" % (pkg_epoch, pkg_ver, pkg_rel)
                if evr_key in self.evr2id_dict and pkg_arch in self.arch2id_dict:
                    packages_names.append(pkg_name)
                    auxiliary_dict[pkg][pkg_name] = []

                    evr_id = self.evr2id_dict[evr_key]
                    packages_evrids.append(evr_id)
                    auxiliary_dict[pkg]['name'] = pkg_name
                    auxiliary_dict[pkg]['evr_id'] = evr_id
                    auxiliary_dict[pkg]['arch_id'] = self.arch2id_dict[pkg_arch]
                    auxiliary_dict[pkg]['repo_id'] = []
                    auxiliary_dict[pkg]['pkg_id'] = []
                    auxiliary_dict[pkg]['update_id'] = []

        response['update_list'] = answer

        if releasever is not None:
            response['relasever'] = releasever
        if basearch is not None:
            response['basearch'] = basearch
        if provided_repo_labels is not None:
            response.update({'repository_list': provided_repo_labels})

        if not packages_evrids:
            return response

        # Select all packages with given evrs ids and put them into dictionary
        self.cursor.execute("select id, name, evr_id, arch_id from package where evr_id in %s;",
                            [tuple(packages_evrids)])
        packs = self.cursor.fetchall()
        nevra2pkg_id = {}
        for oid, name, evr_id, arch_id in packs:
            key = "%s:%s:%s" % (name, evr_id, arch_id)
            nevra2pkg_id.setdefault(key, []).append(oid)

        pkg_ids = []
        for pkg in auxiliary_dict.values():
            try:
                key = "%s:%s:%s" % (pkg['name'],
                                    pkg['evr_id'],
                                    pkg['arch_id'])
                pkg_ids.extend(nevra2pkg_id[key])
                pkg['pkg_id'].extend(nevra2pkg_id[key])
            except KeyError:
                pass

        if not pkg_ids:
            return response

        # Select all repo_id and add mapping to package id
        self.cursor.execute("select pkg_id, repo_id from pkg_repo where pkg_id in %s;", [tuple(pkg_ids)])
        pack_repo_ids = self.cursor.fetchall()
        pkg_id2repo_id = {}

        for pkg_id, repo_id in pack_repo_ids:
            pkg_id2repo_id.setdefault(pkg_id, []).append(repo_id)

        for pkg in auxiliary_dict.values():
            try:
                for pkg_id in pkg['pkg_id']:
                    pkg['repo_id'].extend(pkg_id2repo_id[pkg_id])
            except KeyError:
                pass

        self.cursor.execute("select name, id from package where name in %s;", [tuple(packages_names)])
        sql_result = self.cursor.fetchall()
        names2ids = {}
        for name, oid in sql_result:
            names2ids.setdefault(name, []).append(oid)

        for pkg in auxiliary_dict.values():
            try:
                pkg_name = pkg['name']
                pkg[pkg_name].extend(names2ids[pkg_name])
            except KeyError:
                pass

        update_pkg_ids = []

        sql = """SELECT package.id
                   FROM package
                   JOIN evr ON package.evr_id = evr.id
                  WHERE package.id in %s and evr.evr > (select evr from evr where id = %s)"""
        for pkg in auxiliary_dict.values():
            if pkg:
                pkg_name = pkg['name']
                if pkg_name in pkg and pkg[pkg_name]:
                    self.cursor.execute(sql, [tuple(pkg[pkg_name]),
                                              pkg['evr_id']])

                    for oid in self.cursor.fetchall():
                        pkg['update_id'].append(oid[0])
                        update_pkg_ids.append(oid[0])

        pkg_id2repo_id = {}
        pkg_id2errata_id = {}
        pkg_id2full_name = {}
        pkg_id2arch_id = {}
        all_errata = []

        if update_pkg_ids:
            # Select all info about pkg_id to repo_id for update packages
            self.cursor.execute("select pkg_id, repo_id from pkg_repo where pkg_id in %s;", [tuple(update_pkg_ids)])
            all_pkg_repos = self.cursor.fetchall()
            for pkg_id, repo_id in all_pkg_repos:
                pkg_id2repo_id.setdefault(pkg_id, []).append(repo_id)

            # Select all info about pkg_id to errata_id
            self.cursor.execute("select pkg_id, errata_id from pkg_errata where pkg_id in %s;", [tuple(update_pkg_ids)])
            all_pkg_errata = self.cursor.fetchall()
            for pkg_id, errata_id in all_pkg_errata:
                all_errata.append(errata_id)
                pkg_id2errata_id.setdefault(pkg_id, []).append(errata_id)

            # Select full info about all update packages
            self.cursor.execute("SELECT id, name, evr_id, arch_id from package where id in %s;",
                                [tuple(update_pkg_ids)])
            packages = self.cursor.fetchall()

            for oid, name, evr_id, arch_id in packages:
                full_rpm_name = join_packagename(name,
                                                 self.id2evr_dict[evr_id]['epoch'],
                                                 self.id2evr_dict[evr_id]['version'],
                                                 self.id2evr_dict[evr_id]['release'],
                                                 self.id2arch_dict[arch_id])

                pkg_id2full_name[oid] = full_rpm_name
                pkg_id2arch_id[oid] = arch_id

        if all_errata:
            # Select all info about errata
            self.cursor.execute("SELECT id, name from errata where id in %s;", [tuple(all_errata)])
            errata = self.cursor.fetchall()
            id2errata_dict = {}
            all_errata_id = []
            for oid, name in errata:
                id2errata_dict[oid] = name
                all_errata_id.append(oid)

            self.cursor.execute("SELECT errata_id, repo_id from errata_repo where errata_id in %s",
                                [tuple(all_errata_id)])
            sql_result = self.cursor.fetchall()
            errata_id2repo_id = {}
            for errata_id, repo_id in sql_result:
                errata_id2repo_id.setdefault(errata_id, []).append(repo_id)

            self.cursor.execute("SELECT errata_id, cve_id from errata_cve where errata_id in %s",
                                [tuple(all_errata_id)])
            sql_result = self.cursor.fetchall()
            errata_id2cve_id = {}
            for errata_id, cve_id in sql_result:
                errata_id2cve_id.setdefault(errata_id, []).append(cve_id)

        # Fill the result answer with update information
        for pkg in auxiliary_dict:
            if 'update_id' not in auxiliary_dict[pkg]:
                continue

            for upd_pkg_id in auxiliary_dict[pkg]['update_id']:
                # FIXME: use compatibility tables instead of exact matching
                if auxiliary_dict[pkg]['arch_id'] != pkg_id2arch_id[upd_pkg_id] or \
                                upd_pkg_id not in pkg_id2errata_id:
                    continue

                for r_id in pkg_id2repo_id[upd_pkg_id]:
                    # check if update package in the same repo with original one
                    # and if the list of repositories for updates is provided, also check repo id in this list
                    if r_id not in auxiliary_dict[pkg]['repo_id'] or r_id not in repo_ids:
                        continue

                    errata_ids = pkg_id2errata_id[upd_pkg_id]
                    for e_id in errata_ids:
                        # check current erratum has some linked cve and it is in the same repo with update pkg
                        if e_id in errata_id2cve_id and errata_id2cve_id[e_id] and r_id in errata_id2repo_id[e_id]:
                            e_name = id2errata_dict[e_id]
                            r_label = self.repocache.id2label(r_id)

                            response['update_list'][pkg].append({
                                'package': pkg_id2full_name[upd_pkg_id],
                                'erratum': e_name,
                                'repository': r_label})

        return response
