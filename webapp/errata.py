#!/usr/bin/python3 -u

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

    if filename[-4:] == '.rpm':
        filename = filename[:-4]

    archIndex = filename.rfind('.')
    arch = filename[archIndex + 1:]

    relIndex = filename[:archIndex].rfind('-')
    rel = filename[relIndex + 1:archIndex]

    verIndex = filename[:relIndex].rfind('-')
    ver = filename[verIndex + 1:relIndex]

    epochIndex = filename.find(':')
    if epochIndex == -1:
        epoch = '0'
    else:
        epoch = filename[:epochIndex]

    name = filename[epochIndex + 1:verIndex]
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
            packages_to_process.extend(package_file.readlines())
        packages_to_process = [x.strip() for x in packages_to_process]
        packages_to_process = [x for x in packages_to_process if x]
    elif len(unparsed) >= 1:
        packages_to_process.append(unparsed[0])
    else:
        print("Missing rpm_name or package list file. Exiting.")
        sys.exit(1)

    cursor = init_db(options.db_name, options.db_user, options.db_pass, options.db_host, options.db_port)
    for pkg in packages_to_process:
        res = process(pkg, cursor)

        for item in res:
            print(item)

if __name__ == '__main__':
    main()
