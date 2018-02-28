#!/usr/bin/python -u

"""
known issues

1. strictly follows architecture so things like upgrade from x86_64 to noarch are not possible
2. doesn't follow obsoletes of packages
3. looks only for advisories with CVE associated
4. can be probably written in one select, split into multiple to improve readability of the alrgorithm
5. can be optimized for performance
"""

from optparse import Option, OptionParser

import decimal
import psycopg2
import sys
import ujson

DEFAULT_DB_NAME = "vmaas"
DEFAULT_DB_USER = "vmaas_user"
DEFAULT_DB_PASSWORD = "vmaas_passwd"
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_PORT = 5432


def _dict(row=None, description=None):
  """
  converts array into dict
  @param row: array to be converted
  @param description: array description which will be used as dict keys
  """
  if not description:
    raise AttributeError('Need dictionary description')
  data = {}
  if row is None:
    return None
  for i in range(len(row)):
    if isinstance(row[i], decimal.Decimal):
      data[description[i][0]] = int(row[i])
    else:
      data[description[i][0]] = row[i]
  return data


def splitFilename(filename):
    """
    Pass in a standard style rpm fullname 

    Return a name, version, release, epoch, arch, e.g.::
        foo-1.0-1.i386.rpm returns foo, 1.0, 1, 0, i386
        1:bar-9-123a.ia64.rpm returns bar, 9, 123a, 1, ia64
    """

    isEpoch = True if filename.find(':') != -1 else False

    if filename[-4:] == '.rpm':
        filename = filename[:-4]

    archIndex = filename.rfind('.')
    arch = filename[archIndex + 1:]

    relIndex = filename[:archIndex].rfind('-')
    rel = filename[relIndex + 1:archIndex]

    if isEpoch:
        verIndex = filename[:relIndex].rfind(':')
    else:
        verIndex = filename[:relIndex].rfind('-')
    ver = filename[verIndex + 1:relIndex]


    if isEpoch:
        epochIndex = filename[:verIndex].rfind('-')
        epoch = filename[epochIndex + 1:verIndex]
    else:
        epochIndex = verIndex
        epoch = '0'

    name = filename[:epochIndex]
    return name, ver, rel, epoch, arch

def init_db(db_name, db_user, db_pass, db_host, db_port):
    connection = psycopg2.connect(database=db_name, user=db_user, password=db_pass, host=db_host, port=db_port)
    return connection.cursor()

"""
finds all repos that contain the RPM we're searching for
"""
def get_repos(cur, n, v, r, e, a):
    the_sql = """
        select repo_id, pkg_id
        from pkg_repo
        where (pkg_id in (select id from package where name = %(name)s
        and evr_id = (select id from evr where epoch = %(epoch)s
                      and version = %(version)s and release = %(release)s)
        and arch_id = (select id from arch where name = %(arch)s)))
        """
    cur.execute(the_sql, {'name' : n, 'version' : v, 'release' : r, 'epoch' : e, 'arch' : a})
    res = [_dict(x, cur.description) for x in cur.fetchall()]
    return res

"""
finds all packages with higher nevra present in repos
from RPM logic all packages with higher nevra are upgrades
"""
def get_result(cur, n, v, r, e, a, repos):
    the_sql = """
        select r.name, pr.pkg_id
        from pkg_repo pr join repo r on pr.repo_id = r.id and r.id in %(repos)s
        where pr.pkg_id in (select package.id from package join evr on package.evr_id = evr.id where package.name = %(name)s
        and package.arch_id = (select id from arch where name = %(arch)s)
        and evr.evr > (select evr from evr where (epoch = %(epoch)s and version = %(version)s and release = %(release)s)))
    """
    cur.execute(the_sql, {'name' : n, 'version' : v, 'release' : r, 'epoch' : e, 'arch' : a, 'repos' : repos})
    res = [_dict(x, cur.description) for x in cur.fetchall()]
    return res

"""
returns all advisories which are linked to the upgradeable packages and have associated any CVE
"""
def get_erratas(cur, packages):
    the_sql = """
    select e.name as advisory_name, pe.pkg_id from errata e join pkg_errata pe on e.id = pe.errata_id where pe.pkg_id in %(packages)s and exists (select 1 from errata_cve where errata_id = e.id)
    """
    cur.execute(the_sql, {'packages' : packages})
    res = [_dict(x, cur.description) for x in cur.fetchall()]
    return res

"""
similar to get_erratas with addition of repository and nevra of the package
"""
def get_all(cur, packages):
    the_sql = """
    select e.name as advisory_name, pe.pkg_id, evr.epoch, evr.version, evr.release, r.name as repo_name from errata e join pkg_errata pe on e.id = pe.errata_id left join package p on pe.pkg_id = p.id join evr on p.evr_id = evr.id left join pkg_repo pr on pr.pkg_id = p.id join repo r on r.id = pr.repo_id where pe.pkg_id in %(packages)s and exists (select 1 from errata_cve where errata_id = e.id)
    """
    cur.execute(the_sql, {'packages' : packages})
    res = [_dict(x, cur.description) for x in cur.fetchall()]
    return res

def merge_dict(x, y):
    z = x.copy()
    z.update(y)
    return z

def process(filename, cursor):
    n, v, r, e, a = splitFilename(filename)
    if e == '':
        e = None

    try:
        repos = get_repos(cursor, n, v, r, e, a)
        packages = get_result(cursor, n, v, r, e, a, tuple(set([ x['repo_id'] for x in repos]) or set([None])))
        #res = get_erratas(cursor, tuple(set([ x['pkg_id'] for x in packages]) or set([None])))
        res = get_all(cursor, tuple(set([ x['pkg_id'] for x in packages]) or set([None])))
    except AttributeError:
        return []
    return [ merge_dict(x, {'name' : n}) for x in res ]


def process_list(cursor, packages_to_process):
    auxiliary_dict = {}
    answer = {}

    if not packages_to_process:
        return answer

    # Select all evrs and put them into dictionary
    cursor.execute("SELECT id, epoch, version, release from evr")
    evrs = cursor.fetchall()
    evr2id_dict = {}
    id2evr_dict = {}
    for id, e, v, r in evrs:
        key = e + ':' + v + ':' + r
        evr2id_dict[key] = id
        id2evr_dict[id] = {'epoch': e, 'version': v, 'release': r}

    # Select all archs and put them into dictionary
    cursor.execute("SELECT id, name from arch")
    archs = cursor.fetchall()
    arch2id_dict = {}
    id2arch_dict = {}
    for id, name in archs:
        arch2id_dict[name] = id
        id2arch_dict[id] = name

    packages_names = []
    packages_evrids = []

    for pkg in packages_to_process:
        pkg = str(pkg)

        # process all packages form input
        if pkg not in auxiliary_dict:
            n, v, r, e, a = splitFilename(str(pkg))
            auxiliary_dict[pkg] = {}  # create dictionary with aux data for pkg

            evr_key = e + ':' + v + ':' + r
            if evr_key in evr2id_dict:
                packages_names.append(n)
                auxiliary_dict[pkg][n] = []

                evr_id = evr2id_dict[evr_key]
                packages_evrids.append(evr_id)
                auxiliary_dict[pkg]['evr_id'] = evr_id
                auxiliary_dict[pkg]['arch_id'] = arch2id_dict[a]
                auxiliary_dict[pkg]['repo_id'] = []
                auxiliary_dict[pkg]['pkg_id'] = []
                auxiliary_dict[pkg]['update_id'] = []

    # Select all packages with given evrs ids and put them into dictionary
    cursor.execute("select id, name, evr_id, arch_id from package where evr_id in %s;",  [tuple(packages_evrids)])
    packs = cursor.fetchall()
    nevra2pkg_id = {}
    for id, name, evr_id, arch_id in packs:
        key = name + ':' + str(evr_id) + ':' + str(arch_id)
        if key not in nevra2pkg_id:
            nevra2pkg_id[key] = [id]
        else:
            nevra2pkg_id[key].append(id)

    pkg_ids = []
    for pkg in auxiliary_dict.keys():
        n, v, r, e, a = splitFilename(str(pkg))

        try:
            key = str(n + ':' + str(auxiliary_dict[pkg]['evr_id']) + ':' + str(auxiliary_dict[pkg]['arch_id']))
            pkg_ids.extend(nevra2pkg_id[key])
            auxiliary_dict[pkg]['pkg_id'].extend(nevra2pkg_id[key])
        except KeyError:
            pass

    # Select all repo_id and add mapping to package id
    cursor.execute("select pkg_id, repo_id from pkg_repo where pkg_id in %s;", [tuple(pkg_ids)])
    pack_repo_ids = cursor.fetchall()
    pkg_id2repo_id = {}

    repo_ids = []

    for pkg_id, repo_id in pack_repo_ids:
        repo_ids.append(repo_id)

        if pkg_id in pkg_id2repo_id:
            pkg_id2repo_id[pkg_id].append(repo_id)
        else:
            pkg_id2repo_id[pkg_id] = [repo_id]

    for pkg in auxiliary_dict.keys():
            try:
                for pkg_id in auxiliary_dict[pkg]['pkg_id']:
                    auxiliary_dict[pkg]['repo_id'].extend(pkg_id2repo_id[pkg_id])
            except KeyError:
                pass

    cursor.execute("select name, id from package where name in %s;", [tuple(packages_names)])
    sql_result = cursor.fetchall()
    names2ids = {}
    for name, id in sql_result:

        if name in names2ids:
            names2ids[name].append(id)
        else:
            names2ids[name] = [id]

    for pkg in auxiliary_dict.keys():
        n, v, r, e, a = splitFilename(str(pkg))

        try:
            auxiliary_dict[pkg][n].extend(names2ids[n])
        except KeyError:
            pass

    update_pkg_ids = []

    for pkg in auxiliary_dict:
        n, v, r, e, a = splitFilename(str(pkg))

        if n in auxiliary_dict[pkg] and auxiliary_dict[pkg][n]:
            sql = """
            select package.id from package join evr on package.evr_id = evr.id where package.id in %s and evr.evr > (select evr from evr where id = %s);
            """ % ('%s', str(auxiliary_dict[pkg]['evr_id']))

            cursor.execute(sql, [tuple(auxiliary_dict[pkg][n])])

            for id in cursor.fetchall():
                auxiliary_dict[pkg]['update_id'].append(id[0])
                update_pkg_ids.append(id[0])

    # Select all info about repos
    cursor.execute("select id, name, url from repo where id in %s;", [tuple(repo_ids)])
    all_repos = cursor.fetchall()
    repoinfo_dict = {}
    for id, name, url in all_repos:
        repoinfo_dict[id] = {'name': name, 'url': url}

    # Select all info about pkg_id to repo_id
    cursor.execute("select pkg_id, repo_id from pkg_repo where pkg_id in %s;", [tuple(update_pkg_ids)])
    all_pkg_repos = cursor.fetchall()
    pkg_id2repo_id = {}
    for pkg_id, repo_id in all_pkg_repos:

        if pkg_id not in pkg_id2repo_id:
            pkg_id2repo_id[pkg_id] = [repo_id]
        else:
            pkg_id2repo_id[pkg_id].append(repo_id)

    # Select all info about pkg_id to errata_id
    cursor.execute("select pkg_id, errata_id from pkg_errata where pkg_id in %s;", [tuple(update_pkg_ids)])
    all_pkg_errata = cursor.fetchall()
    pkg_id2errata_id = {}
    all_errata = []
    for pkg_id, errata_id in all_pkg_errata:
        all_errata.append(errata_id)
        if pkg_id not in pkg_id2errata_id:
            pkg_id2errata_id[pkg_id] = [errata_id]
        else:
            pkg_id2errata_id[pkg_id].append(errata_id)

    # Select all info about errata
    cursor.execute("SELECT id, name from errata where id in %s;", [tuple(all_errata)])
    errata = cursor.fetchall()
    id2errata_dict = {}
    all_errata_id = []
    for id, name in errata:
        id2errata_dict[id] = name
        all_errata_id.append(id)

    cursor.execute("SELECT errata_id, repo_id from errata_repo where errata_id in %s;", [tuple(all_errata_id)])
    sql_result = cursor.fetchall()
    errata_id2repo_id = {}
    for errata_id, repo_id in sql_result:
        errata_id2repo_id[errata_id] = repo_id

    # Select all info about packages
    cursor.execute("SELECT id, name, evr_id, arch_id from package where id in %s;", [tuple(update_pkg_ids)])
    packages = cursor.fetchall()
    id2pakage_dict = {}
    for id, name, evr_id, arch_id in packages:
        full_rpm_name = name + '-'
        if id2evr_dict[evr_id]['epoch'] != '0':
            full_rpm_name += id2evr_dict[evr_id]['epoch'] + ':'
        full_rpm_name += id2evr_dict[evr_id]['version'] + '-' + id2evr_dict[evr_id]['release'] + '.' + id2arch_dict[arch_id]

        id2pakage_dict[id] = full_rpm_name

    for pkg in auxiliary_dict:
        answer[pkg] = []
        try:
            for upd_pkg_id in auxiliary_dict[pkg]['update_id']:

                errata_ids = pkg_id2errata_id[upd_pkg_id]

                for e_id in errata_ids:
                    e_name = id2errata_dict[e_id]
                    r_id = errata_id2repo_id[e_id]
                    r_name = repoinfo_dict[r_id]['name']
                    answer[pkg].append([id2pakage_dict[upd_pkg_id], e_name, r_name])
        except KeyError:
            pass

    return answer


def main():
    optionsTable = [
        Option('-d', '--dbname', action='store', dest='db_name', default=DEFAULT_DB_NAME,
            help='database name to connect to (default: "rhnschema")'),
        Option('-U', '--username', action='store', dest='db_user', default=DEFAULT_DB_USER,
            help='database user name (default: "rhnuser")'),
        Option('-W', '--password', action='store', dest='db_pass', default=DEFAULT_DB_PASSWORD,
            help='password to use (default: "rhnuser")'),
        Option('--host', action='store', dest='db_host', default=DEFAULT_DB_HOST,
            help='database server host or socket directory (default: "local socket")'),
        Option('-p', '--port', action='store', dest='db_port', default=DEFAULT_DB_PORT,
            help='database server port (default: "5432")'),
        Option('--pkgfile', action='store', dest='pkgfile',
            help='read package names from file'),
    ]

    optionParser = OptionParser(
        usage="Usage: %s [--dbname=<dbname>] [--username=<username>] [--password=<password>] [--host=<host>] [--port=<port>] rpm_name" % sys.argv[0],
        option_list=optionsTable)

    options, unparsed = optionParser.parse_args(sys.argv[1:])

    packages_to_process = []

    if options.pkgfile:
        with open(options.pkgfile, "r") as package_file:
            data = ujson.loads(package_file.read())
            packages_to_process.extend(set(data['package_list']))

    elif len(unparsed) >= 1:
        packages_to_process.append(unparsed[0])
    else:
        print("Missing rpm_name or package list file. Exiting.")
        sys.exit(1)

    cursor = init_db(options.db_name, options.db_user, options.db_pass, options.db_host, options.db_port)
    answer = process_list(cursor, packages_to_process)
    print(ujson.dumps(answer))

if __name__ == '__main__':
    main()
