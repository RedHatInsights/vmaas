#!/usr/bin/env python3
"""
Tool for exporting preprocessed data from database for webapp nodes.
"""

import glob
import os
import shelve
from common.logging_utils import get_logger, init_logging
from common.dateutil import format_datetime, now
from common.fileutil import remove_file_if_exists
from database.database_handler import DatabaseHandler, NamedCursor, init_db

DEFAULT_KEEP_COPIES = "2"
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
        self.keep_copies = int(os.getenv('KEEP_COPIES', DEFAULT_KEEP_COPIES))

    @staticmethod
    def fetch_latest_dump():
        """Read the symlink, to know what is latest dump."""
        try:
            return os.readlink(DUMP).split("-", 1)[1]
        except FileNotFoundError:
            return None

    def _named_cursor(self):
        return NamedCursor(self.db_instance)

    def dump(self):
        """Dump necessary data tu disk file"""
        timestamp = format_datetime(now())
        dump_filename = "%s-%s" % (self.filename, timestamp)
        LOGGER.info("Exporting data to %s", dump_filename)
        try:
            with shelve.open(dump_filename, 'c') as dump:
                self._dump_packagename(dump)
                self._dump_content_set_with_pkg_names(dump)
                self._dump_all_content_sets(dump)
                self._dump_cpes(dump)
                self._dump_updates(dump)
                self._dump_evr(dump)
                self._dump_arch(dump)
                self._dump_arch_compat(dump)
                self._dump_package_details(dump)
                self._dump_repo(dump)
                self._dump_errata(dump)
                self._dump_cves(dump)
                self._dump_modules(dump)
                self._dump_oval(dump)
                self._dump_dbchange(dump)
                dump["dbchange:exported"] = timestamp
        except Exception:  # pylint: disable=broad-except
            # database exceptions caught here
            LOGGER.exception("Failed to create dbdump")
            remove_file_if_exists(dump_filename)
        else:
            # relink to the latest file only if no db exceptions
            remove_file_if_exists(self.filename)
            os.symlink(dump_filename, self.filename)
            # remove old data above limit
            old_data = sorted(glob.glob("%s-*" % self.filename), reverse=True)
            for fname in old_data[self.keep_copies:]:
                LOGGER.info("Removing old dump %s", fname)
                remove_file_if_exists(fname)

    def _dump_packagename(self, dump):
        """Select all package names"""
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct pn.id, pn.name
                                from package_name pn inner join
                                     package p on pn.id = p.name_id
                            """)
            for name_id, pkg_name in cursor:
                dump["packagename2id:%s" % pkg_name] = name_id
                dump["id2packagename:%s" % name_id] = pkg_name
                self.packagename_ids.append(name_id)

    def _dump_content_set_with_pkg_names(self, dump):
        """Select all packages"""
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct p.name_id, cs.id
                                from package p
                          inner join pkg_repo pr on p.id = pr.pkg_id
                          inner join repo r on pr.repo_id = r.id
                          inner join content_set cs on r.content_set_id = cs.id""")
            pkg_name_ids = {}
            for name_id, content_set_id in cursor:
                pkg_name_ids.setdefault("content_set_id2pkg_name_ids:%s" % content_set_id, []).append(name_id)
            dump.update(pkg_name_ids)
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct pn.id, cs.id
                                from package_name pn
                             inner join package p on pn.id = p.name_id
                             inner join package p2 on p2.source_package_id = p.id
                             inner join package_name bpn on p2.name_id = bpn.id
                             inner join pkg_repo on pkg_repo.pkg_id = p2.id
                             inner join repo on repo.id = pkg_repo.repo_id
                             inner join content_set cs on cs.id = repo.content_set_id""")
            cs_ids = {}
            for src_name_id, content_set_id in cursor:
                cs_ids.setdefault("src_pkg_name_id2cs_ids:%s" % src_name_id, []).append(content_set_id)
            dump.update(cs_ids)

    def _dump_all_content_sets(self, dump):
        """Select all content sets"""
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct cs.label, cs.id from content_set cs""")
            for label, content_set_id in cursor:
                dump["content_set_id2label:%s" % content_set_id] = label
                dump["label2content_set_id:%s" % label] = content_set_id

    def _dump_cpes(self, dump):
        """Select all CPEs and mappings to content sets"""
        with self._named_cursor() as cursor:
            cursor.execute("""select id, label from cpe""")
            for cpe_id, label in cursor:
                dump["cpe_id2label:%s" % cpe_id] = label
                dump["label2cpe_id:%s" % label] = cpe_id

        with self._named_cursor() as cursor:
            cursor.execute("""select cpe_id, content_set_id
                                from cpe_content_set
                            """)
            content_set_id2cpe_ids = {}
            for cpe_id, content_set_id in cursor:
                content_set_id2cpe_ids.setdefault("content_set_id2cpe_ids:%s" % content_set_id, []).append(cpe_id)
            dump.update(content_set_id2cpe_ids)

    def _dump_updates(self, dump):
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

    def _dump_evr(self, dump):
        """Select all evrs and put them into dictionary"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, epoch, version, release from evr")
            for evr_id, epoch, ver, rel in cursor:
                dump["evr2id:%s:%s:%s" % (epoch, ver, rel)] = evr_id
                dump["id2evr:%s" % evr_id] = (epoch, ver, rel)

    def _dump_arch(self, dump):
        """Select all archs and put them into dictionary"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, name from arch")
            for arch_id, name in cursor:
                dump["arch2id:%s" % name] = arch_id
                dump["id2arch:%s" % arch_id] = name

    def _dump_arch_compat(self, dump):
        """Select information about archs compatibility"""
        with self._named_cursor() as cursor:
            cursor.execute("select from_arch_id, to_arch_id from arch_compatibility")
            arch_compat = {}
            for from_arch_id, to_arch_id in cursor:
                arch_compat.setdefault("arch_compat:%s" % from_arch_id, set()).add(to_arch_id)
            dump.update(arch_compat)

    def _dump_package_details(self, dump):
        """Select details about packages (for previously selected package names)"""
        if self.packagename_ids:
            with self._named_cursor() as cursor:
                cursor.execute("""select id, name_id, evr_id, arch_id, summary, description, source_package_id
                                    from package
                                   where name_id in %s
                               """, [tuple(self.packagename_ids)])
                src_pkg_id2pkg_ids = dict()
                for pkg_id, name_id, evr_id, arch_id, summary, description, source_package_id in cursor:
                    sum_id = hash(summary)
                    desc_id = hash(description)
                    dump["strings:%s" % sum_id] = summary
                    dump["strings:%s" % desc_id] = description
                    dump["package_details:%s" % pkg_id] = (name_id, evr_id, arch_id, sum_id, desc_id,
                                                           source_package_id or 0)
                    dump["nevra2pkgid:%s:%s:%s" % (name_id, evr_id, arch_id)] = pkg_id

                    self.package_ids.append(pkg_id)
                    if source_package_id is not None:
                        src_pkg_id2pkg_ids.setdefault("src_pkg_id2pkg_ids:%s" % source_package_id, []).append(pkg_id)
                dump.update(src_pkg_id2pkg_ids)

    def _dump_repo(self, dump):
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
                                      r.revision,
                                      cs.third_party
                                 from repo r
                                 join content_set cs on cs.id = r.content_set_id
                                 left join arch a on a.id = r.basearch_id
                                 join product p on p.id = cs.product_id
                                 """)
            repolabel2ids = {}
            for oid, label, name, url, basearch, releasever, product, product_id, revision, third_party in cursor:
                dump["repo_detail:%s" % oid] = (label, name, url, basearch,
                                                releasever, product, product_id,
                                                format_datetime(revision), third_party)
                repolabel2ids.setdefault("repolabel2ids:%s" % label, []).append(oid)
            dump.update(repolabel2ids)

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

    def _dump_errata(self, dump):  # pylint: disable=too-many-branches
        """Select errata mappings"""
        # Select errata ID to name mapping
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct e.id, e.name
                                from errata e
                          inner join errata_type et on e.errata_type_id = et.id
                           left join errata_cve ec on e.id = ec.errata_id
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

            # Select errata detail for errata API
            errataid2cves = {}
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT errata_cve.errata_id, cve.name
                                    FROM cve
                                    JOIN errata_cve ON cve_id = cve.id
                                   WHERE errata_id in %s AND cve.source_id IS NOT NULL
                               """, [tuple(self.errata_ids)])
                for errata_id, cve_name in cursor:
                    errataid2cves.setdefault(errata_id, []).append(cve_name)
            errataid2pkgid = {}
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT errata_id, pkg_id FROM pkg_errata
                                   WHERE errata_id in %s
                               """, [tuple(self.errata_ids)])
                for errata_id, pkg_id in cursor:
                    errataid2pkgid.setdefault(errata_id, []).append(pkg_id)
            errataid2bzs = {}
            errataid2refs = {}
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT errata_id, type, name FROM errata_refs
                                   WHERE errata_id in %s
                               """, [tuple(self.errata_ids)])
                for errata_id, ref_type, ref_name in cursor:
                    if ref_type == 'bugzilla':
                        errataid2bzs.setdefault(errata_id, []).append(ref_name)
                    else:
                        errataid2refs.setdefault(errata_id, []).append(ref_name)

            # Select errata ID to module mapping
            errataid2modules = {}
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT distinct p.errata_id, module.name,
                                  m.stream_name, m.version, m.context
                                  FROM module_stream m
                                  LEFT JOIN module on m.module_id = module.id
                                  LEFT JOIN pkg_errata p ON module_stream_id = m.id
                                  LEFT JOIN package_name on p.pkg_id = package_name.id
                                  WHERE p.module_stream_id IS NOT NULL
                                  AND p.errata_id in %s""", [tuple(self.errata_ids)])
                for errata_id, module_name, module_stream_name, module_version, module_context in cursor:
                    errataid2modules.setdefault(errata_id, []).append({"module_name": module_name,
                                                                       "module_stream": module_stream_name,
                                                                       "module_version": module_version,
                                                                       "module_context": module_context,
                                                                       "package_list": [],
                                                                       "source_package_list": []})
            # Select module to package ID mapping
            modules2pkgid = {}
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT distinct errata_id, pkg_id
                                  FROM pkg_errata
                                  WHERE module_stream_id is not null
                                  AND errata_id in %s""", [tuple(self.errata_ids)])
                for errata_id, pkg_id in cursor:
                    modules2pkgid.setdefault(errata_id, []).append(pkg_id)
            for errata_id in modules2pkgid:
                for module in modules2pkgid[errata_id]:
                    errataid2modules[errata_id][0]["package_list"].append(module)

            # Now pull all the data together for the dump
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT errata.id, errata.name, synopsis, summary,
                                         errata_type.name, errata_severity.name,
                                         description, solution, issued, updated, 
                                         true = ANY (
                                            SELECT cs.third_party
                                            FROM errata_repo er
                                            JOIN repo r ON er.repo_id = r.id
                                            JOIN content_set cs ON cs.id = r.content_set_id
                                            WHERE er.errata_id = errata.id
                                         ) AS third_party
                                    FROM errata
                                    JOIN errata_type ON errata_type_id = errata_type.id
                                    LEFT JOIN errata_severity ON severity_id = errata_severity.id
                                   WHERE errata.id in %s
                               """, [tuple(self.errata_ids)])
                for errata_id, e_name, synopsis, summary, e_type, e_severity, \
                    description, solution, issued, updated, third_party in cursor:
                    url = "https://access.redhat.com/errata/%s" % e_name
                    dump["errata_detail:%s" % e_name] = (synopsis, summary, e_type,
                                                         e_severity, description,
                                                         solution, issued, updated,
                                                         errataid2cves.get(errata_id, []),
                                                         errataid2pkgid.get(errata_id, []),
                                                         errataid2bzs.get(errata_id, []),
                                                         errataid2refs.get(errata_id, []),
                                                         errataid2modules.get(errata_id, []),
                                                         url, third_party)

    def _dump_cves(self, dump):
        """Select cve details"""
        # Select CWE to CVE mapping
        cveid2cwe = {}
        with self._named_cursor() as cursor:
            cursor.execute("""select cve_cwe.cve_id, cwe.name
                                from cve_cwe cve_cwe
                                join cwe cwe on cve_cwe.cwe_id = cwe.id
                                join cve cve on cve.id = cve_cwe.cve_id
                                where cve.source_id is not null
                           """)
            for cve_id, cwe in cursor:
                cveid2cwe.setdefault(cve_id, []).append(cwe)

        # Select CVE to package-id mapping
        cveid2pid = {}
        with self._named_cursor() as cursor:
            cursor.execute("""
                            select distinct cve.id as cve_id, pe.pkg_id
                              from cve cve
                                   inner join errata_cve ec on cve.id = ec.cve_id
                                   inner join pkg_errata pe on ec.errata_id = pe.errata_id
                              where cve.source_id is not null
                            order by cve.id, pe.pkg_id
                           """)
            for cve_id, pkg_id in cursor:
                cveid2pid.setdefault(cve_id, []).append(pkg_id)

        # Select CVE to errata-ID mapping
        cveid2eid = {}
        with self._named_cursor() as cursor:
            cursor.execute("""
                           select ec.cve_id as cve_id, ec.errata_id
                             from errata_cve ec
                             join cve c on ec.cve_id = c.id
                             where c.source_id is not null
                           order by ec.cve_id, ec.errata_id
                           """)
            for cve_id, errata_id in cursor:
                cveid2eid.setdefault(cve_id, []).append(errata_id)

        # Pull everything together
        with self._named_cursor() as cursor:
            cursor.execute("""select cve.id,
                                     cve.name,
                                     cve.redhat_url,
                                     cve.secondary_url,
                                     cve.cvss3_score,
                                     cve.cvss3_metrics,
                                     cve_impact.name as impact,
                                     cve.published_date,
                                     cve.modified_date,
                                     cve.iava,
                                     cve.description,
                                     cve.cvss2_score,
                                     cve.cvss2_metrics,
                                     cve_source.name as source
                                from cve
                           join cve_source on cve.source_id = cve_source.id
                           left join cve_impact on cve.impact_id = cve_impact.id
                           """)
            for cve_id, name, redhat_url, secondary_url, \
                cvss3_score, cvss3_metrics, \
                impact, published_date, modified_date, iava, description, \
                cvss2_score, cvss2_metrics, source in cursor:
                dump["cve_detail:%s" % name] = (redhat_url, secondary_url, cvss3_score, cvss3_metrics,
                                                impact, published_date, modified_date, iava, description,
                                                cveid2cwe.get(cve_id, []),
                                                cveid2pid.get(cve_id, []),
                                                cveid2eid.get(cve_id, []),
                                                cvss2_score, cvss2_metrics, source)

    def _dump_modules(self, dump):
        """Select module information"""
        if self.errata_ids:
            with self._named_cursor() as cursor:
                cursor.execute("""select pkg_id,
                                         errata_id,
                                         module_stream_id as module_id
                                    from pkg_errata
                                   where module_stream_id is not null
                                     and errata_id in %s
                            """, [tuple(self.errata_ids)])
                pkg2module = {}
                for pkg_id, errata_id, module_id in cursor:
                    pkg2module.setdefault("pkgerrata2module:%s:%s" % (pkg_id, errata_id), set()).add(module_id)
                dump.update(pkg2module)

        with self._named_cursor() as cursor:
            cursor.execute("""select m.name,
                                     s.stream_name,
                                     s.id as stream_id
                                from module_stream s
                                join module m on s.module_id = m.id
                           """)
            modulename2id = {}
            for name, stream_name, stream_id in cursor:
                modulename2id.setdefault("modulename2id:%s:%s" % (name, stream_name), set()).add(stream_id)
            dump.update(modulename2id)

    def _dump_oval(self, dump):
        """Select OVAL information"""
        with self._named_cursor() as cursor:
            cursor.execute("""select cpe_id, definition_id from oval_definition_cpe""")
            cpe_id2ovaldefinition_ids = {}
            for cpe_id, oval_definition_id in cursor:
                cpe_id2ovaldefinition_ids.setdefault(
                    "cpe_id2ovaldefinition_ids:%s" % cpe_id, []).append(oval_definition_id)
            dump.update(cpe_id2ovaldefinition_ids)


        with self._named_cursor() as cursor:
            cursor.execute("""select distinct d.id, o.package_name_id
                              from oval_definition d join
                                   oval_definition_test dt on d.id = dt.definition_id join
                                   oval_rpminfo_test t on dt.rpminfo_test_id = t.id join
                                   oval_rpminfo_object o on t.rpminfo_object_id = o.id""")
            packagename_id2definition_ids = {}
            for oval_definition_id, package_name_id in cursor:
                packagename_id2definition_ids.setdefault(
                    "packagename_id2definition_ids:%s" % package_name_id, []).append(oval_definition_id)
            dump.update(packagename_id2definition_ids)

        with self._named_cursor() as cursor:
            cursor.execute("""select d.id, d.definition_type_id, d.criteria_id
                              from oval_definition d""")
            for oval_definition_id, oval_definition_type_id, oval_definition_criteria_id in cursor:
                dump["ovaldefinition_detail:%s" % oval_definition_id] = \
                    (oval_definition_type_id, oval_definition_criteria_id)

        with self._named_cursor() as cursor:
            cursor.execute("""select dc.definition_id, cve.name
                              from oval_definition_cve dc join
                                   cve on dc.cve_id = cve.id""")
            ovaldefinition_id2cves = {}
            for oval_definition_id, cve_name in cursor:
                ovaldefinition_id2cves.setdefault(
                    "ovaldefinition_id2cves:%s" % oval_definition_id, []).append(cve_name)
            dump.update(ovaldefinition_id2cves)

        with self._named_cursor() as cursor:
            cursor.execute("""select c.id, c.operator_id
                              from oval_criteria c""")
            for oval_criteria_id, type_id in cursor:
                dump["ovalcriteria_id2type:%s" % oval_criteria_id] = type_id

        with self._named_cursor() as cursor:
            cursor.execute("""select parent_criteria_id, dep_criteria_id, dep_test_id
                              from oval_criteria_dependency""")
            ovalcriteria_id2depcriteria_ids = {}
            ovalcriteria_id2deptest_ids = {}
            for parent_criteria_id, dep_criteria_id, dep_test_id in cursor:
                if dep_test_id is None:
                    ovalcriteria_id2depcriteria_ids.setdefault(
                        "ovalcriteria_id2depcriteria_ids:%s" % parent_criteria_id, []).append(dep_criteria_id)
                else:
                    ovalcriteria_id2deptest_ids.setdefault(
                        "ovalcriteria_id2deptest_ids:%s" % parent_criteria_id, []).append(dep_test_id)
            dump.update(ovalcriteria_id2depcriteria_ids)
            dump.update(ovalcriteria_id2deptest_ids)

        with self._named_cursor() as cursor:
            # Ignoring oval_check_rpminfo table as it cointains only one row currently used by all tests
            cursor.execute("""select t.id, o.package_name_id, t.check_existence_id
                              from oval_rpminfo_test t join
                                   oval_rpminfo_object o on t.rpminfo_object_id = o.id""")
            for oval_test_id, package_name_id, check_existence_id in cursor:
                dump["ovaltest_detail:%s" % oval_test_id] = (package_name_id, check_existence_id)

        with self._named_cursor() as cursor:
            cursor.execute("""select ts.rpminfo_test_id, s.id, s.evr_id, s.evr_operation_id
                              from oval_rpminfo_test_state ts join
                                   oval_rpminfo_state s on ts.rpminfo_state_id = s.id
                              where s.evr_id is not null
                                and s.evr_operation_id is not null""")
            ovaltest_id2states = {}
            for oval_test_id, oval_state_id, evr_id, oval_operation_evr_id in cursor:
                ovaltest_id2states.setdefault("ovaltest_id2states:%s" % oval_test_id, []).append(
                    (oval_state_id, evr_id, oval_operation_evr_id))
            dump.update(ovaltest_id2states)

        with self._named_cursor() as cursor:
            cursor.execute("""select rpminfo_state_id, arch_id from oval_rpminfo_state_arch""")
            ovalstate_id2arches = {}
            for oval_state_id, arch_id in cursor:
                ovalstate_id2arches.setdefault("ovalstate_id2arches:%s" % oval_state_id, set()).add(arch_id)
            dump.update(ovalstate_id2arches)

    def _dump_dbchange(self, dump):
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
    data = DataDump(db_instance, filename)
    data.dump()


if __name__ == '__main__':
    main(DUMP)
