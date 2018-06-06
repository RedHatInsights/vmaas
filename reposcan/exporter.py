#!/usr/bin/python3
"""
Tool for exporting preprocessed data from database for webapp nodes.
"""

import shelve
from common.logging import get_logger, init_logging
from common.dateutil import format_datetime
from database.database_handler import DatabaseHandler, NamedCursor, init_db

DUMP = '/data/vmaas.dbm'
LOGGER = get_logger(__name__)


class DataDump:
    """Class for creating disk dump from database."""
    def __init__(self, db_instance, filename):
        self.db_instance = db_instance
        self.filename = filename
        self.packagename_ids = []
        self.package_ids = []
        self.errata_ids = []

    def _named_cursor(self):
        return NamedCursor(self.db_instance)

    def dump(self):
        """Dump necessary data tu disk file"""
        with shelve.open(self.filename, 'c') as dump:
            self.dump_packagename(dump)
            self.dump_updates(dump)
            self.dump_evr(dump)
            self.dump_arch(dump)
            self.dump_arch_compat(dump)
            self.dump_package_details(dump)
            self.dump_repo(dump)
            self.dump_errata(dump)
            self.dump_cves(dump)
            self.dump_dbchange(dump)

    def dump_packagename(self, dump):
        """Select all package names (only for package names with ever received sec. update)"""
        with self._named_cursor() as cursor:
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
                dump["packagename2id:%s" % pkg_name] = name_id
                dump["id2packagename:%s" % name_id] = pkg_name
                self.packagename_ids.append(name_id)

    def dump_updates(self, dump):
        """Select ordered updates lists for previously selected package names"""
        if self.packagename_ids:
            with self._named_cursor() as cursor:
                cursor.execute("""select p.name_id, p.id, p.evr_id
                                    from package p
                              inner join evr on p.evr_id = evr.id
                                   where p.name_id in %s
                                   order by p.name_id, evr.evr
                                """, [tuple(self.packagename_ids)])
                index_cnt = {}
                updates = {}
                updates_index = {}
                for name_id, pkg_id, evr_id in cursor:
                    idx = index_cnt.get(name_id, 0)
                    updates.setdefault("updates:%s" % name_id, []).append(pkg_id)
                    updates_index.setdefault("updates_index:%s" % name_id,
                                             {}).setdefault(evr_id, []).append(idx)
                    idx += 1
                    index_cnt[name_id] = idx
                dump.update(updates)
                dump.update(updates_index)

    def dump_evr(self, dump):
        """Select all evrs and put them into dictionary"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, epoch, version, release from evr")
            for evr_id, epoch, ver, rel in cursor:
                dump["evr2id:%s:%s:%s" % (epoch, ver, rel)] = evr_id
                dump["id2evr:%s" % evr_id] = (epoch, ver, rel)

    def dump_arch(self, dump):
        """Select all archs and put them into dictionary"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, name from arch")
            for arch_id, name in cursor:
                dump["arch2id:%s" % name] = arch_id
                dump["id2arch:%s" % arch_id] = name

    def dump_arch_compat(self, dump):
        """Select information about archs compatibility"""
        with self._named_cursor() as cursor:
            cursor.execute("select from_arch_id, to_arch_id from arch_compatibility")
            arch_compat = {}
            for from_arch_id, to_arch_id in cursor:
                arch_compat.setdefault("arch_compat:%s" % from_arch_id, set()).add(to_arch_id)
            dump.update(arch_compat)

    def dump_package_details(self, dump):
        """Select details about packages (for previously selected package names)"""
        if self.packagename_ids:
            with self._named_cursor() as cursor:
                cursor.execute("""select id, name_id, evr_id, arch_id, summary, description
                                    from package
                                   where name_id in %s
                               """, [tuple(self.packagename_ids)])
                for pkg_id, name_id, evr_id, arch_id, summary, description in cursor:
                    dump["package_details:%s" % pkg_id] = (name_id, evr_id, arch_id, summary, description)
                    self.package_ids.append(pkg_id)

    def dump_repo(self, dump):
        """Select repo mappings"""

        # Select repo detail mapping
        with self._named_cursor() as cursor:
            cursor.execute("""select r.id,
                                      cs.label,
                                      cs.name as repo_name,
                                      r.url,
                                      a.name as basearch_name,
                                      r.releasever,
                                      p.name as product_name,
                                      p.id as product_id,
                                      r.revision
                                 from repo r
                                 join content_set cs on cs.id = r.content_set_id
                                 join arch a on a.id = r.basearch_id
                                 join product p on p.id = cs.product_id
                                 """)
            repolabel2ids = {}
            productid2repoids = {}
            for oid, label, name, url, basearch, releasever, product, product_id, revision in cursor:
                dump["repo_detail:%s" % oid] = (label, name, url, basearch,
                                                releasever, product, product_id,
                                                format_datetime(revision))
                repolabel2ids.setdefault("repolabel2ids:%s" % label, []).append(oid)
                productid2repoids.setdefault("productid2repoids:%s" % product_id, []).append(oid)
            dump.update(repolabel2ids)
            dump.update(productid2repoids)

        if self.package_ids:
            # Select package ID to repo IDs mapping
            with self._named_cursor() as cursor:
                cursor.execute("""select pkg_id, repo_id
                                    from pkg_repo
                                   where pkg_id in %s
                               """, [tuple(self.package_ids)])
                pkgid2repoids = {}
                for pkg_id, repo_id in cursor:
                    pkgid2repoids.setdefault("pkgid2repoids:%s" % pkg_id, []).append(repo_id)
                dump.update(pkgid2repoids)

    def dump_errata(self, dump):
        """Select errata mappings"""
        # Select errata ID to name mapping
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct e.id, e.name
                                from errata e
                          inner join errata_type et on e.errata_type_id = et.id
                           left join errata_cve ec on e.id = ec.errata_id
                               where et.name = 'security' or ec.cve_id is not null
                           """)
            for errata_id, errata_name in cursor:
                dump["errataid2name:%s" % errata_id] = errata_name
                self.errata_ids.append(errata_id)

        if self.errata_ids:
            # Select package ID to errata IDs mapping, only for relevant errata
            with self._named_cursor() as cursor:
                cursor.execute("""select pkg_id, errata_id
                                    from pkg_errata
                                   where errata_id in %s
                                """, [tuple(self.errata_ids)])
                pkgid2errataids = {}
                for pkg_id, errata_id in cursor:
                    pkgid2errataids.setdefault("pkgid2errataids:%s" % pkg_id, set()).add(errata_id)
                dump.update(pkgid2errataids)

            # Select errata ID to repo IDs mapping, only for relevant errata
            with self._named_cursor() as cursor:
                cursor.execute("""select errata_id, repo_id
                                    from errata_repo
                                   where errata_id in %s
                                """, [tuple(self.errata_ids)])
                errataid2repoids = {}
                for errata_id, repo_id in cursor:
                    errataid2repoids.setdefault("errataid2repoids:%s" % errata_id,
                                                set()).add(repo_id)
                dump.update(errataid2repoids)

    def dump_cves(self, dump):
        """Select cve details"""
        # Select CWE to CVE mapping
        cveid2cwe = {}
        with self._named_cursor() as cursor:
            cursor.execute("""select cve_id, cwe.name
                                from cve_cwe
                                join cwe on cve_cwe.cwe_id = cwe.id
                           """)
            for cve_id, cwe in cursor:
                cveid2cwe.setdefault(cve_id, []).append(cwe)

        # Select errata ID to name mapping
        with self._named_cursor() as cursor:
            cursor.execute("""select cve.id,
                                     cve.name,
                                     cve.redhat_url,
                                     cve.secondary_url,
                                     cve.cvss3_score,
                                     cve_impact.name as impact,
                                     cve.published_date,
                                     cve.modified_date,
                                     cve.iava,
                                     cve.description
                                from cve
                           left join cve_impact on cve.impact_id = cve_impact.id
                           """)
            for cve_id, name, redhat_url, secondary_url, cvss3_score, impact, \
                published_date, modified_date, iava, description in cursor:
                dump["cve_detail:%s" % name] = (redhat_url, secondary_url, cvss3_score, impact,
                                                published_date, modified_date, iava, description,
                                                cveid2cwe.get(cve_id, []))

    def dump_dbchange(self, dump):
        """Select db change details"""
        with self._named_cursor() as cursor:
            cursor.execute("""select errata_changes,
                                     cve_changes,
                                     repository_changes,
                                     last_change
                                from dbchange""")
            row = cursor.fetchone()
            dump["dbchange:errata_changes"] = row[0]
            dump["dbchange:cve_changes"] = row[1]
            dump["dbchange:repository_changes"] = row[2]
            dump["dbchange:last_change"] = row[3]


def main(filename):
    """ Main loop."""
    init_logging()
    init_db()
    db_instance = DatabaseHandler.get_connection()
    #data = DataDump(db.cursor(), filename)
    data = DataDump(db_instance, filename)
    data.dump()

if __name__ == '__main__':
    main(DUMP)
