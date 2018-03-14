"""
Module to handle /updates API calls.
"""

def split_filename(filename):
    """
    Pass in a standard style rpm fullname

    Return a name, version, release, epoch, arch, e.g.::
        foo-1.0-1.i386.rpm returns foo, 1.0, 1, 0, i386
        bar-1:9-123a.ia64.rpm returns bar, 9, 123a, 1, ia64
    """

    is_epoch = True if filename.find(':') != -1 else False

    if filename[-4:] == '.rpm':
        filename = filename[:-4]

    arch_index = filename.rfind('.')
    arch = filename[arch_index + 1:]

    rel_index = filename[:arch_index].rfind('-')
    rel = filename[rel_index + 1:arch_index]

    if is_epoch:
        ver_index = filename[:rel_index].rfind(':')
    else:
        ver_index = filename[:rel_index].rfind('-')
    ver = filename[ver_index + 1:rel_index]


    if is_epoch:
        epoch_index = filename[:ver_index].rfind('-')
        epoch = filename[epoch_index + 1:ver_index]
    else:
        epoch_index = ver_index
        epoch = '0'

    name = filename[:epoch_index]
    return name, ver, rel, epoch, arch


class UpdatesAPI(object):
    """ Main /updates API class. """
    def __init__(self, cursor):
        self.cursor = cursor
        self.evr2id_dict = {}
        self.id2evr_dict = {}
        self.arch2id_dict = {}
        self.id2arch_dict = {}

        self.prepare()

    def prepare(self):
        """ Read ahead table of keys. """
        # Select all evrs and put them into dictionary
        # pylint: disable=invalid-name
        self.cursor.execute("SELECT id, epoch, version, release from evr")
        evrs = self.cursor.fetchall()
        for oid, e, v, r in evrs:
            key = e + ':' + v + ':' + r
            self.evr2id_dict[key] = oid
            self.id2evr_dict[oid] = {'epoch': e, 'version': v, 'release': r}

        # Select all archs and put them into dictionary
        self.cursor.execute("SELECT id, name from arch")
        archs = self.cursor.fetchall()
        for oid, name in archs:
            self.arch2id_dict[name] = oid
            self.id2arch_dict[oid] = name


    def process_list(self, data):
        #pylint: disable=too-many-locals,too-many-branches,too-many-statements,too-many-nested-blocks
        """
        This method is looking for updates of a package, including name of package to update to,
        associated erratum and repository this erratum is from.

        :param packages_to_process: list of package to find updates for every of them

        :returns: updates for a package in format of list of dictionaries {'package': <p_name>, 'erratum': <e_name>,
        'repository': <r_name>}

        """
        # pylint: disable=invalid-name

        packages_to_process = data['package_list']
        auxiliary_dict = {}
        answer = {}

        if not packages_to_process:
            return answer

        provided_repo_ids = None
        provided_repo_names = None

        if 'repository_list' in data:
            provided_repo_names = data['repository_list']

            if provided_repo_names:
                provided_repo_ids = []
                self.cursor.execute("select id from repo where name in %s;", [tuple(provided_repo_names)])
                for id_tuple in self.cursor.fetchall():
                    for oid in id_tuple:
                        provided_repo_ids.append(oid)

        packages_names = []
        packages_evrids = []

        for pkg in packages_to_process:
            pkg = str(pkg)

            # process all packages form input
            if pkg not in auxiliary_dict:
                n, v, r, e, a = split_filename(str(pkg))
                auxiliary_dict[pkg] = {}  # fill auxiliary dictionary with empty data for every package
                answer[pkg] = []          # fill answer with empty data

                evr_key = e + ':' + v + ':' + r
                if evr_key in self.evr2id_dict:
                    packages_names.append(n)
                    auxiliary_dict[pkg][n] = []

                    evr_id = self.evr2id_dict[evr_key]
                    packages_evrids.append(evr_id)
                    auxiliary_dict[pkg]['evr_id'] = evr_id
                    auxiliary_dict[pkg]['arch_id'] = self.arch2id_dict[a]
                    auxiliary_dict[pkg]['repo_id'] = []
                    auxiliary_dict[pkg]['pkg_id'] = []
                    auxiliary_dict[pkg]['update_id'] = []

        response = {
            'update_list': answer,
        }

        if provided_repo_ids is not None:
            response.update({'repository_list': provided_repo_names})

        if not packages_evrids:
            return response

        # Select all packages with given evrs ids and put them into dictionary
        self.cursor.execute("select id, name, evr_id, arch_id from package where evr_id in %s;",
                            [tuple(packages_evrids)])
        packs = self.cursor.fetchall()
        nevra2pkg_id = {}
        for oid, name, evr_id, arch_id in packs:
            key = name + ':' + str(evr_id) + ':' + str(arch_id)
            if key not in nevra2pkg_id:
                nevra2pkg_id[key] = [oid]
            else:
                nevra2pkg_id[key].append(oid)

        pkg_ids = []
        for pkg in auxiliary_dict:
            n, v, r, e, a = split_filename(str(pkg))

            try:
                key = str(n + ':' + str(auxiliary_dict[pkg]['evr_id']) + ':' + str(auxiliary_dict[pkg]['arch_id']))
                pkg_ids.extend(nevra2pkg_id[key])
                auxiliary_dict[pkg]['pkg_id'].extend(nevra2pkg_id[key])
            except KeyError:
                pass

        if not pkg_ids:
            return response

        # Select all repo_id and add mapping to package id
        self.cursor.execute("select pkg_id, repo_id from pkg_repo where pkg_id in %s;", [tuple(pkg_ids)])
        pack_repo_ids = self.cursor.fetchall()
        pkg_id2repo_id = {}

        repo_ids = []

        for pkg_id, repo_id in pack_repo_ids:
            repo_ids.append(repo_id)

            if pkg_id in pkg_id2repo_id:
                pkg_id2repo_id[pkg_id].append(repo_id)
            else:
                pkg_id2repo_id[pkg_id] = [repo_id]

        for pkg in auxiliary_dict:
            try:
                for pkg_id in auxiliary_dict[pkg]['pkg_id']:
                    auxiliary_dict[pkg]['repo_id'].extend(pkg_id2repo_id[pkg_id])
            except KeyError:
                pass

        self.cursor.execute("select name, id from package where name in %s;", [tuple(packages_names)])
        sql_result = self.cursor.fetchall()
        names2ids = {}
        for name, oid in sql_result:

            if name in names2ids:
                names2ids[name].append(oid)
            else:
                names2ids[name] = [oid]

        for pkg in auxiliary_dict:
            n, v, r, e, a = split_filename(str(pkg))

            try:
                auxiliary_dict[pkg][n].extend(names2ids[n])
            except KeyError:
                pass

        update_pkg_ids = []

        sql = """SELECT package.id
                   FROM package
                   JOIN evr ON package.evr_id = evr.id
                  WHERE package.id in %s and evr.evr > (select evr from evr where id = %s)"""
        for pkg in auxiliary_dict:
            n, v, r, e, a = split_filename(str(pkg))

            if n in auxiliary_dict[pkg] and auxiliary_dict[pkg][n]:
                self.cursor.execute(sql, [tuple(auxiliary_dict[pkg][n]),
                                          auxiliary_dict[pkg]['evr_id']])

                for oid in self.cursor.fetchall():
                    auxiliary_dict[pkg]['update_id'].append(oid[0])
                    update_pkg_ids.append(oid[0])

        # Select all info about repos
        self.cursor.execute("select id, name, url from repo where id in %s;", [tuple(repo_ids)])
        all_repos = self.cursor.fetchall()
        repoinfo_dict = {}
        for oid, name, url in all_repos:
            repoinfo_dict[oid] = {'name': name, 'url': url}

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

                if pkg_id not in pkg_id2repo_id:
                    pkg_id2repo_id[pkg_id] = [repo_id]
                else:
                    pkg_id2repo_id[pkg_id].append(repo_id)

            # Select all info about pkg_id to errata_id
            self.cursor.execute("select pkg_id, errata_id from pkg_errata where pkg_id in %s;", [tuple(update_pkg_ids)])
            all_pkg_errata = self.cursor.fetchall()
            for pkg_id, errata_id in all_pkg_errata:
                all_errata.append(errata_id)
                if pkg_id not in pkg_id2errata_id:
                    pkg_id2errata_id[pkg_id] = [errata_id]
                else:
                    pkg_id2errata_id[pkg_id].append(errata_id)

            # Select full info about all update packages
            self.cursor.execute("SELECT id, name, evr_id, arch_id from package where id in %s;",
                                [tuple(update_pkg_ids)])
            packages = self.cursor.fetchall()

            for oid, name, evr_id, arch_id in packages:
                full_rpm_name = name + '-'
                if self.id2evr_dict[evr_id]['epoch'] != '0':
                    full_rpm_name += self.id2evr_dict[evr_id]['epoch'] + ':'
                full_rpm_name += self.id2evr_dict[evr_id]['version'] + '-' + \
                                 self.id2evr_dict[evr_id]['release'] + '.' + \
                                 self.id2arch_dict[arch_id]

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

            self.cursor.execute("SELECT errata_id, repo_id from errata_repo where errata_id in %s;", [tuple(all_errata_id)])
            sql_result = self.cursor.fetchall()
            errata_id2repo_id = {}
            for errata_id, repo_id in sql_result:
                if errata_id not in errata_id2repo_id:
                    errata_id2repo_id[errata_id] = [repo_id]
                else:
                    errata_id2repo_id[errata_id].append(repo_id)

        # Fill the result answer with update information
        for pkg in auxiliary_dict:
            if 'update_id' not in auxiliary_dict[pkg]:
                continue

            for upd_pkg_id in auxiliary_dict[pkg]['update_id']:
                # FIXME: use compatibility tables instead of exact matching
                if auxiliary_dict[pkg]['arch_id'] == pkg_id2arch_id[upd_pkg_id]:
                    for r_id in pkg_id2repo_id[upd_pkg_id]:
                        # check if update package in the same repo with original one
                        # and if the list of repositories for updates is provided, also check repo id in this list
                        if r_id in auxiliary_dict[pkg]['repo_id'] and \
                                (provided_repo_ids is None or r_id in provided_repo_ids):
                            # Some pkgs don't have associated errata (eg, original-repo-content)
                            if upd_pkg_id in pkg_id2errata_id:
                                errata_ids = pkg_id2errata_id[upd_pkg_id]
                                for e_id in errata_ids:
                                    # check current errata in the same repo with update pkg
                                    if r_id in errata_id2repo_id[e_id]:
                                        e_name = id2errata_dict[e_id]
                                        r_name = repoinfo_dict[r_id]['name']

                                        response['update_list'][pkg].append({
                                            'package': pkg_id2full_name[upd_pkg_id],
                                            'erratum': e_name,
                                            'repository': r_name})


        return response
