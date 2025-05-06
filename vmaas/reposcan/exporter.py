#!/usr/bin/env python3
"""
Tool for exporting preprocessed data from database for webapp nodes.
"""

# pylint: disable=too-many-lines

import glob
import json
import os
import sqlite3

import zstandard as zstd

from boto3 import client as boto3_client
from botocore.exceptions import ClientError

from vmaas.common.config import Config
from vmaas.common.logging_utils import get_logger, init_logging
from vmaas.common.date_utils import format_datetime, now
from vmaas.common.fileutil import remove_file_if_exists
from vmaas.reposcan.database.database_handler import DatabaseHandler, NamedCursor, init_db

DEFAULT_KEEP_COPIES = "2"
DUMP = '/data/vmaas.db'
DUMP_COMPRESSED = f"{DUMP}.zstd"
DUMP_SCHEMA_VERSION = 5
LOGGER = get_logger(__name__)
CFG = Config()


class S3UploadError(Exception):
    """S3 Error exception."""


def fetch_latest_dump():
    """Read the symlink, to know what is latest dump."""
    try:
        return os.readlink(DUMP).split("-", 1)[1]
    except FileNotFoundError:
        return None


def upload_dump_s3():
    """Upload DB dump to S3 bucket."""
    try:
        client = boto3_client(
            "s3",
            endpoint_url=CFG.dump_s3_url,
            aws_access_key_id=CFG.dump_s3_access_key,
            aws_secret_access_key=CFG.dump_s3_secret_key,
            use_ssl=CFG.dump_s3_tls,
        )
    except ClientError as err:
        raise S3UploadError("Failed to create boto3 client") from err

    try:
        cctx = zstd.ZstdCompressor()
        with open(DUMP, "rb") as ifd, open(DUMP_COMPRESSED, "wb") as ofd:
            cctx.copy_stream(ifd, ofd)
    except (ValueError, MemoryError, zstd.ZstdError) as err:
        raise S3UploadError("Failed to compress vmaas.db") from err

    try:
        client.upload_file(
            Filename=DUMP_COMPRESSED,
            Bucket=CFG.dump_bucket_name,
            Key="vmaas.db.zstd",
        )
    except ClientError as err:
        raise S3UploadError("Failed to upload vmaas.db to s3") from err


class SqliteDump:
    """Class for creating sqlite disk dump from database."""

    def __init__(self, db_instance, filename):
        self.db_instance = db_instance
        self.filename = filename
        self.packagename_ids = []
        self.package_ids = []
        self.errata_ids = []
        self.keep_copies = int(os.getenv('KEEP_COPIES', DEFAULT_KEEP_COPIES))

    def _named_cursor(self):
        return NamedCursor(self.db_instance)

    def dump(self, timestamp):
        """Dump necessary data to disk file"""
        dump_filename = "%s-%s" % (self.filename, timestamp)
        LOGGER.info("Exporting data to %s", dump_filename)
        try:
            with sqlite3.connect(dump_filename) as sqlite_conn:
                dump = sqlite_conn.cursor()
                self._dump_content_sets(dump)
                self._dump_packagename(dump)
                self._dump_content_set_pkgnames(dump)
                self._dump_content_set_src_pkg_names(dump)
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
                self._dump_csaf(dump)
                self._dump_os_releases(dump)
                self._dump_release_graph(dump)
                self._dump_dbchange(dump, timestamp)
                self._dump_dump_schema_version(dump)
        except Exception as err:  # pylint: disable=broad-except
            # database exceptions caught here
            LOGGER.exception("Failed to create dbdump", exc_info=err)
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

    def _dump_content_set_src_pkg_names(self, dump):
        """Select all packages"""
        dump.execute("""
            create table if not exists content_set_src_pkg_name (
                content_set_id integer not null,
                src_pkg_name_id integer not null,
                primary key (content_set_id, src_pkg_name_id)
            )""")

        with self._named_cursor() as cursor:
            cursor.execute("""select distinct pn.id, cs.id
                                from package_name pn
                             inner join package p on pn.id = p.name_id
                             inner join package p2 on p2.source_package_id = p.id
                             inner join package_name bpn on p2.name_id = bpn.id
                             inner join pkg_repo on pkg_repo.pkg_id = p2.id
                             inner join repo on repo.id = pkg_repo.repo_id
                             inner join content_set cs on cs.id = repo.content_set_id""")

            for name_id, content_set_id in cursor:
                dump.execute("""
                    insert into content_set_src_pkg_name values (?, ?)""", (content_set_id, name_id))

    def _dump_content_set_pkgnames(self, dump):
        """ Export a table linking package names to content sets in which they appear"""
        dump.execute("""
           create table if not exists content_set_pkg_name (
                 content_set_id integer not null,
                 pkg_name_id integer not null,
                 primary key (content_set_id, pkg_name_id)
           )""")

        with self._named_cursor() as cursor:
            cursor.execute("""select distinct p.name_id, cs.id
                                       from package p
                                 inner join pkg_repo pr on p.id = pr.pkg_id
                                 inner join repo r on pr.repo_id = r.id
                                 inner join content_set cs on r.content_set_id = cs.id""")
            for name_id, content_set_id in cursor:
                dump.execute("insert into content_set_pkg_name values (?, ?)", (content_set_id, name_id))

    def _dump_content_sets(self, dump):
        """Export a table containing content set metadata"""
        dump.execute("""
            create table if not exists content_set (
                  id integer primary key not null,
                  label text not null check ( label <> '' )
            )""")

        with self._named_cursor() as cursor:
            cursor.execute("""select distinct cs.label, cs.id from content_set cs""")
            for label, content_set_id in cursor:
                dump.execute("""insert into content_set values(?, ?)""", (content_set_id, label))

    def _dump_cpes(self, dump):
        """Select all CPEs and mappings to content sets"""
        dump.execute("""
            create table if not exists cpe (
                id integer primary key  not null ,
                label text unique not null check ( label <> '' )
            )""")

        with self._named_cursor() as cursor:
            cursor.execute("""select id, label from cpe""")
            for cpe_id, label in cursor:
                dump.execute("""insert into cpe values(?, ?)""", (cpe_id, label))

        dump.execute("""
            create table if not exists cpe_content_set(
                cpe_id integer not null,
                content_set_id integer not null,
                primary key (cpe_id, content_set_id)
            )""")

        with self._named_cursor() as cursor:
            cursor.execute("""select cpe_id, content_set_id
                                   from cpe_content_set
                               """)
            for cpe_id, content_set_id in cursor:
                dump.execute("insert into cpe_content_set values(?, ?)", (cpe_id, content_set_id))

        dump.execute("""
            create table if not exists cpe_repo(
                cpe_id integer not null,
                repo_id integer not null,
                primary key (cpe_id, repo_id)
            )""")

        with self._named_cursor() as cursor:
            cursor.execute("""select cpe_id, repo_id
                                   from cpe_repo
                               """)
            for cpe_id, repo_id in cursor:
                dump.execute("insert into cpe_repo values(?, ?)", (cpe_id, repo_id))

    def _dump_packagename(self, dump):
        """Select all package names (only for package names with ever received sec. update)"""
        dump.execute("""create table if not exists packagename (
                                id integer primary key,
                                packagename text
                                )""")
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct pn.id, pn.name
                                from package_name pn inner join
                                     package p on pn.id = p.name_id
                            """)
            for name_id, pkg_name in cursor:
                dump.execute("insert into packagename values (?, ?)", (name_id, pkg_name))
                self.packagename_ids.append(name_id)

    def _dump_updates(self, dump):
        """Select ordered updates lists for previously selected package names"""
        dump.execute("""create table if not exists updates (
                                    name_id integer,
                                    package_id integer,
                                    package_order integer
                                )""")
        dump.execute("""create table if not exists updates_index (
                                    name_id integer,
                                    evr_id integer,
                                    package_order integer
                                    )""")
        if self.packagename_ids:
            with self._named_cursor() as cursor:
                cursor.execute("""select p.name_id, p.id, p.evr_id
                                    from package p
                              inner join evr on p.evr_id = evr.id
                                   where p.name_id in %s
                                   order by p.name_id, evr.evr
                                """, [tuple(self.packagename_ids)])
                index_cnt = {}
                for name_id, pkg_id, evr_id in cursor:
                    idx = index_cnt.get(name_id, 0)
                    dump.execute("insert into updates values (?, ?, ?)", (name_id, pkg_id, idx))
                    dump.execute("insert into updates_index values (?, ?, ?)", (name_id, evr_id, idx))
                    idx += 1
                    index_cnt[name_id] = idx

    def _dump_evr(self, dump):
        """Select all evrs and put them into dictionary"""
        dump.execute("""create table if not exists evr (
                                id integer primary key,
                                epoch integer,
                                version text,
                                release text
                                )""")
        with self._named_cursor() as cursor:
            cursor.execute("select id, epoch, version, release from evr")
            for evr_id, epoch, ver, rel in cursor:
                dump.execute("insert into evr values (?, ?, ?, ?)", (evr_id, epoch, ver, rel))

    def _dump_arch(self, dump):
        """Select all archs and put them into dictionary"""
        dump.execute("""create table if not exists arch (
                                id integer primary key,
                                arch text
                               )""")
        with self._named_cursor() as cursor:
            cursor.execute("select id, name from arch")
            for arch_id, name in cursor:
                dump.execute("insert into arch values (?, ?)", (arch_id, name))

    def _dump_arch_compat(self, dump):
        """Select information about archs compatibility"""
        dump.execute("""create table if not exists arch_compat (
                                from_arch_id integer,
                                to_arch_id integer
                               )""")
        with self._named_cursor() as cursor:
            cursor.execute("select from_arch_id, to_arch_id from arch_compatibility")
            for from_arch_id, to_arch_id in cursor:
                dump.execute("insert into arch_compat values (?, ?)", (from_arch_id, to_arch_id))

    def _dump_package_details(self, dump):
        """Select details about packages (for previously selected package names)"""
        dump.execute("""create table if not exists string (
                                id integer primary key,
                                string text
                               )""")
        dump.execute("""create table if not exists package_detail (
                                id integer primary key,
                                name_id integer,
                                evr_id integer,
                                arch_id integer,
                                summary_id integer,
                                description_id integer,
                                source_package_id integer,
                                modified timestamp
                               )""")
        if self.packagename_ids:
            with self._named_cursor() as cursor:
                cursor.execute("""select id, name_id, evr_id, arch_id, summary, description, source_package_id, modified
                                    from package
                                   where name_id in %s
                               """, [tuple(self.packagename_ids)])
                for pkg_id, name_id, evr_id, arch_id, summary, description, source_package_id, modified in cursor:
                    sum_id = hash(summary)
                    desc_id = hash(description)
                    dump.execute("insert or ignore into string values (?, ?)", (sum_id, summary))
                    dump.execute("insert or ignore into string values (?, ?)", (desc_id, description))
                    dump.execute("insert into package_detail values (?, ?, ?, ?, ?, ?, ?, ?)",
                                 (pkg_id, name_id, evr_id, arch_id, sum_id, desc_id, source_package_id, modified))

                    self.package_ids.append(pkg_id)

    def _dump_repo(self, dump):
        """Select repo mappings"""
        dump.execute("""create table if not exists repo_detail (
                                id integer primary key,
                                label text,
                                name text,
                                url text,
                                basearch text,
                                releasever text,
                                product text,
                                product_id integer,
                                revision text,
                                last_change text,
                                third_party integer,
                                organization text
                               )""")
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
                                      r.last_change,
                                      cs.third_party,
                                      o.name
                                 from repo r
                                 join content_set cs on cs.id = r.content_set_id
                                 left join arch a on a.id = r.basearch_id
                                 join product p on p.id = cs.product_id
                                 join organization o on o.id = r.org_id
                                 """)
            for oid, label, name, url, basearch, releasever, \
                    product, product_id, revision, last_change, third_party, organization in cursor:
                dump.execute("insert into repo_detail values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (oid, label, name, url, basearch,
                              releasever, product, product_id,
                              # Use NULLs in export
                              format_datetime(revision) if revision is not None else None,
                              format_datetime(last_change),
                              1 if third_party else 0, organization),)

        dump.execute("""create table if not exists pkg_repo (
                                pkg_id integer,
                                repo_id integer,
                                primary key (pkg_id, repo_id)
                               ) without rowid""")
        if self.package_ids:
            # Select package ID to repo IDs mapping
            with self._named_cursor() as cursor:
                cursor.execute("""select pkg_id, repo_id
                                    from pkg_repo
                                   where pkg_id in %s
                               """, [tuple(self.package_ids)])
                for pkg_id, repo_id in cursor:
                    dump.execute("insert into pkg_repo values (?, ?)", (pkg_id, repo_id))

    def _dump_errata(self, dump):  # pylint: disable=too-many-branches
        """Select errata mappings"""
        # Select errata ID to name mapping
        dump.execute("""create table if not exists errata_detail (
                                id integer primary key,
                                name text,
                                synopsis text,
                                summary text,
                                type text,
                                severity text,
                                description text,
                                solution text,
                                issued text,
                                updated text,
                                url text,
                                third_party integer,
                                requires_reboot boolean
                               )""")
        with self._named_cursor() as cursor:
            cursor.execute("""select distinct e.id
                                from errata e
                          inner join errata_type et on e.errata_type_id = et.id
                           left join errata_cve ec on e.id = ec.errata_id
                           """)
            for errata_id in cursor:
                self.errata_ids.append(errata_id)

        dump.execute("""create table if not exists pkg_errata (
                                pkg_id integer,
                                errata_id integer,
                                primary key (pkg_id, errata_id)
                                ) without rowid""")
        dump.execute("""create table if not exists errata_repo (
                                errata_id integer,
                                repo_id integer,
                                primary key(errata_id, repo_id)
                                ) without rowid""")
        dump.execute("""create table if not exists errata_cve (
                                errata_id integer,
                                cve text,
                                primary key(errata_id, cve)
                               ) without rowid""")
        dump.execute("""create table if not exists errata_refs (
                                errata_id integer,
                                ref text
                               )""")
        dump.execute("""create table if not exists errata_bugzilla (
                                errata_id integer,
                                bugzilla text
                               )""")
        dump.execute("""create table if not exists errata_module (
                                errata_id integer,
                                module_name text,
                                module_stream_id integer,
                                module_stream text,
                                module_version integer,
                                module_context text
                               )""")
        dump.execute("""create table if not exists errata_modulepkg (
                                errata_id integer,
                                module_stream_id integer,
                                pkg_id integer,
                                primary key(errata_id, module_stream_id, pkg_id)
                               )""")
        if self.errata_ids:
            # Select package ID to errata IDs mapping, only for relevant errata
            with self._named_cursor() as cursor:
                cursor.execute("""select pkg_id, errata_id
                                    from pkg_errata
                                   where errata_id in %s
                                """, [tuple(self.errata_ids)])
                for pkg_id, errata_id in cursor:
                    dump.execute("insert or ignore into pkg_errata values (?, ?)", (pkg_id, errata_id))

            # Select errata ID to repo IDs mapping, only for relevant errata
            with self._named_cursor() as cursor:
                cursor.execute("""select errata_id, repo_id
                                    from errata_repo
                                   where errata_id in %s
                                """, [tuple(self.errata_ids)])
                for errata_id, repo_id in cursor:
                    dump.execute("insert or ignore into errata_repo values (?, ?)", (errata_id, repo_id))

            # Select errata detail for errata API
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT errata_cve.errata_id, cve.name
                                    FROM cve
                                    JOIN errata_cve ON cve_id = cve.id
                                   WHERE errata_id in %s
                               """, [tuple(self.errata_ids)])
                for errata_id, cve_name in cursor:
                    dump.execute("insert or ignore into errata_cve values (?, ?)", (errata_id, cve_name))

            with self._named_cursor() as cursor:
                cursor.execute("""SELECT errata_id, type, name FROM errata_refs
                                   WHERE errata_id in %s
                               """, [tuple(self.errata_ids)])
                for errata_id, ref_type, ref_name in cursor:
                    if ref_type == 'bugzilla':
                        dump.execute("insert into errata_bugzilla values (?, ?)", (errata_id, ref_name))
                    else:
                        dump.execute("insert into errata_refs values (?, ?)", (errata_id, ref_name))

            # Select errata ID to module mapping
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT distinct p.errata_id, module.name,
                                  m.id, m.stream_name, m.version, m.context
                                  FROM module_stream m
                                  LEFT JOIN module on m.module_id = module.id
                                  LEFT JOIN pkg_errata p ON module_stream_id = m.id
                                  LEFT JOIN package_name on p.pkg_id = package_name.id
                                  WHERE p.module_stream_id IS NOT NULL
                                  AND p.errata_id in %s""", [tuple(self.errata_ids)])
                for errata_id, module_name, module_stream_id, module_stream_name, \
                        module_version, module_context in cursor:
                    dump.execute("insert into errata_module values (?, ?, ?, ?, ?, ?)",
                                 (errata_id, module_name, module_stream_id, module_stream_name,
                                  module_version, module_context))
            # Select module to package ID mapping
            with self._named_cursor() as cursor:
                cursor.execute("""SELECT distinct errata_id, module_stream_id, pkg_id
                                  FROM pkg_errata
                                  WHERE module_stream_id is not null
                                  AND errata_id in %s""", [tuple(self.errata_ids)])
                for errata_id, module_stream_id, pkg_id in cursor:
                    dump.execute("insert into errata_modulepkg values (?, ?, ?)",
                                 (errata_id, module_stream_id, pkg_id))

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
                                         ) AS third_party, requires_reboot
                                    FROM errata
                                    JOIN errata_type ON errata_type_id = errata_type.id
                                    LEFT JOIN errata_severity ON severity_id = errata_severity.id
                                   WHERE errata.id in %s
                               """, [tuple(self.errata_ids)])
                for errata_id, e_name, synopsis, summary, e_type, e_severity, \
                        description, solution, issued, updated, third_party, requires_reboot in cursor:
                    url = "https://access.redhat.com/errata/%s" % e_name
                    dump.execute("insert into errata_detail values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                                 (errata_id, e_name, synopsis, summary, e_type,
                                  e_severity, description, solution,
                                  format_datetime(issued) if issued is not None else None,
                                  format_datetime(updated) if updated is not None else None,
                                  url, 1 if third_party else 0, requires_reboot)
                                 )

    def _dump_cves(self, dump):
        """Select cve details"""
        dump.execute("""create table if not exists cve_cwe (
                                cve_id integer,
                                cwe text
                               )""")
        dump.execute("""create table if not exists cve_pkg (
                                cve_id integer,
                                pkg_id integer
                               )""")
        dump.execute("""create table if not exists cve_detail (
                                id integer primary key ,
                                name text,
                                redhat_url text,
                                secondary_url text,
                                cvss3_score float,
                                cvss3_metrics text,
                                impact text,
                                published_date text,
                                modified_date text,
                                iava text,
                                description text,
                                cvss2_score float,
                                cvss2_metrics text,
                                source text
                               )""")
        # Select CWE to CVE mapping
        with self._named_cursor() as cursor:
            cursor.execute("""select cve_id, cwe.name
                                from cve_cwe
                                join cwe on cve_cwe.cwe_id = cwe.id
                           """)
            for cve_id, cwe in cursor:
                dump.execute("insert into cve_cwe values (?, ?)", (cve_id, cwe))

        # Select CVE to package-id mapping
        with self._named_cursor() as cursor:
            cursor.execute("""
                            select distinct cve.id as cve_id, pe.pkg_id
                              from cve cve
                                   inner join errata_cve ec on cve.id = ec.cve_id
                                   inner join pkg_errata pe on ec.errata_id = pe.errata_id
                            order by cve.id, pe.pkg_id
                           """)
            for cve_id, pkg_id in cursor:
                dump.execute("insert into cve_pkg values (?, ?)", (cve_id, pkg_id))

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
                cvss3_score = (float(cvss3_score) if cvss3_score is not None else None)
                cvss2_score = (float(cvss2_score) if cvss2_score is not None else None)
                dump.execute("insert into cve_detail values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                             (cve_id, name, redhat_url, secondary_url, cvss3_score, cvss3_metrics, impact,
                              format_datetime(published_date) if published_date is not None else None,
                              format_datetime(modified_date) if modified_date is not None else None,
                              iava, description, cvss2_score, cvss2_metrics, source)
                             )

    def _dump_modules(self, dump):
        """Select module information"""
        dump.execute("""create table if not exists module_stream (
                                stream_id integer,
                                module text,
                                stream text
                               )""")
        with self._named_cursor() as cursor:
            cursor.execute("""select m.name,
                                     s.stream_name,
                                     s.id as stream_id
                                from module_stream s
                                join module m on s.module_id = m.id
                           """)
            for name, stream_name, stream_id in cursor:
                dump.execute("insert into module_stream values (?, ?, ?)", (stream_id, name, stream_name))

        dump.execute("""create table if not exists module_stream_require (
                                stream_id integer,
                                require_id integer
                               )""")
        with self._named_cursor() as cursor:
            cursor.execute("""select module_stream_id,
                                     require_id
                                from module_stream_require
                           """)
            for stream_id, require_id in cursor:
                dump.execute("insert into module_stream_require values (?, ?)", (stream_id, require_id))

    def _dump_csaf(self, dump):
        """Select CSAF data"""
        # Dump data from csaf_product table
        dump.execute("""CREATE TABLE IF NOT EXISTS csaf_product (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cpe_id INTEGER NOT NULL,
                        package_name_id INTEGER DEFAULT 0,
                        package_id INTEGER DEFAULT 0,
                        module_stream TEXT DEFAULT ''
                    )""")
        with self._named_cursor() as cursor:
            cursor.execute("""SELECT id, cpe_id, package_name_id, package_id, module_stream
                            FROM csaf_product""")
            for csaf_product_id, cpe_id, package_name_id, package_id, module_stream in cursor:
                dump.execute("INSERT INTO csaf_product VALUES (?, ?, COALESCE(?, 0), COALESCE(?, 0), COALESCE(?, ''))",
                             (csaf_product_id, cpe_id, package_name_id, package_id, module_stream))

        # Dump data from csaf_cve_product table
        dump.execute("""CREATE TABLE IF NOT EXISTS csaf_cve_product (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        cve_id INTEGER NOT NULL,
                        csaf_product_id INTEGER NOT NULL,
                        csaf_product_status_id INTEGER NOT NULL,
                        erratum TEXT)
                    """)
        with self._named_cursor() as cursor:
            cursor.execute("""SELECT id, cve_id, csaf_product_id, csaf_product_status_id, erratum
                            FROM csaf_cve_product""")
            for csaf_cve_id, cve_id, csaf_product_id, csaf_product_status_id, erratum in cursor:
                dump.execute("INSERT INTO csaf_cve_product VALUES (?, ?, ?, ?, ?)",
                             (csaf_cve_id, cve_id, csaf_product_id, csaf_product_status_id, erratum))

        # Dump data from csaf_product_status table
        dump.execute("""CREATE TABLE IF NOT EXISTS csaf_product_status (
                        id INTEGER PRIMARY KEY NOT NULL,
                        name TEXT UNIQUE NOT NULL)""")
        with self._named_cursor() as cursor:
            cursor.execute("""SELECT id, name
                            FROM csaf_product_status""")
            for csaf_status_id, name in cursor:
                dump.execute("INSERT INTO csaf_product_status VALUES (?, ?)", (csaf_status_id, name))

    def _dump_os_releases(self, dump):
        """Select all OS releases and put them into dictionary"""
        dump.execute("""CREATE TABLE IF NOT EXISTS operating_system (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        major INTEGER NOT NULL,
                        minor INTEGER NOT NULL,
                        lifecycle_phase TEXT NOT NULL,
                        system_profile JSONB NOT NULL)
                    """)
        with self._named_cursor() as cursor:
            cursor.execute("SELECT id, name, major, minor, lifecycle_phase, system_profile FROM operating_system")
            for os_id, name, major, minor, lifecycle_phase, system_profile in cursor:
                dump.execute("INSERT INTO operating_system VALUES (?, ?, ?, ?, ?, ?)", (os_id, name, major, minor, lifecycle_phase, json.dumps(system_profile)))

    def _dump_release_graph(self, dump):
        """Select all release graphs and put them into dictionary without checksum"""
        dump.execute("""CREATE TABLE IF NOT EXISTS release_graph (
                        id INTEGER PRIMARY KEY,
                        name TEXT NOT NULL,
                        graph JSONB NOT NULL)
                     """)
        with self._named_cursor() as cur:
            # checksum is not going to be used by the dump consumer therefore it is excluded in the dump
            cur.execute("SELECT id, name, graph FROM release_graph")
            for _id, name, graph in cur:
                dump.execute("INSERT INTO release_graph VALUES (?, ?, ?)", (_id, name, json.dumps(graph)))

    def _dump_dbchange(self, dump, timestamp):
        """Select db change details"""
        dump.execute("""create table if not exists dbchange (
                                errata_changes text,
                                cve_changes text,
                                repository_changes text,
                                last_change text,
                                exported text
                               )""")
        with self._named_cursor() as cursor:
            cursor.execute("""select errata_changes,
                                     cve_changes,
                                     repository_changes,
                                     last_change
                                from dbchange""")
            row = cursor.fetchone()
            dump.execute("insert into dbchange values (?, ?, ?, ?, ?)", (
                format_datetime(row[0]) if row[0] is not None else None,
                format_datetime(row[1]) if row[1] is not None else None,
                format_datetime(row[2]) if row[2] is not None else None,
                format_datetime(row[3]) if row[3] is not None else None,
                timestamp
            ))

    def _dump_dump_schema_version(self, dump):
        """Put dump schema version number into dump"""
        dump.execute("""CREATE TABLE IF NOT EXISTS dump_schema (
                        version INTEGER NOT NULL)
                     """)
        dump.execute("INSERT INTO dump_schema VALUES (?)", (DUMP_SCHEMA_VERSION,))


def main():
    """ Main loop."""
    init_logging()
    init_db()
    db_instance = DatabaseHandler.get_connection()
    timestamp = format_datetime(now())

    data = SqliteDump(db_instance, DUMP)
    data.dump(timestamp)


if __name__ == '__main__':
    main()
