"""
Module to cache data from file dump.
"""
import array
import asyncio
import datetime
from urllib.parse import urlparse
import sqlite3

import requests

from vmaas.common.config import Config
from vmaas.common.date_utils import parse_datetime
from vmaas.common.logging_utils import get_logger

CFG = Config()
DUMP = '/data/vmaas.db'
DEFAULT_CHUNK_SIZE = 1048576

# repo_detail indexes
REPO_LABEL = 0
REPO_NAME = 1
REPO_URL = 2
REPO_BASEARCH = 3
REPO_RELEASEVER = 4
REPO_PRODUCT = 5
REPO_PRODUCT_ID = 6
REPO_REVISION = 7
REPO_LAST_CHANGE = 8
REPO_THIRD_PARTY = 9

# package detail indexes
PKG_NAME_ID = 0
PKG_EVR_ID = 1
PKG_ARCH_ID = 2
PKG_SUMMARY_ID = 3
PKG_DESC_ID = 4
PKG_SOURCE_PKG_ID = 5
PKG_MODIFIED_ID = 6

# cve detail indexes
CVE_REDHAT_URL = 0
CVE_SECONDARY_URL = 1
CVE_CVSS3_SCORE = 2
CVE_CVSS3_METRICS = 3
CVE_IMPACT = 4
CVE_PUBLISHED_DATE = 5
CVE_MODIFIED_DATE = 6
CVE_IAVA = 7
CVE_DESCRIPTION = 8
CVE_CWE = 9
CVE_PID = 10
CVE_EID = 11
CVE_CVSS2_SCORE = 12
CVE_CVSS2_METRICS = 13
CVE_SOURCE = 14

# errata detail indexes
ERRATA_SYNOPSIS = 0
ERRATA_SUMMARY = 1
ERRATA_TYPE = 2
ERRATA_SEVERITY = 3
ERRATA_DESCRIPTION = 4
ERRATA_SOLUTION = 5
ERRATA_ISSUED = 6
ERRATA_UPDATED = 7
ERRATA_CVE = 8
ERRATA_PKGIDS = 9
ERRATA_BUGZILLA = 10
ERRATA_REFERENCE = 11
ERRATA_MODULE = 12
ERRATA_URL = 13
ERRATA_THIRD_PARTY = 14
ERRATA_REQUIRES_REBOOT = 15
ERRATA_ID = 16

LOGGER = get_logger(__name__)


def as_long_arr(data):
    """Make a native i64 array from list of ints"""
    arr = array.array('q')
    arr.fromlist(data)
    return arr


class Cache:
    """ Cache class. """

    # pylint: disable=too-many-instance-attributes,invalid-name
    def __init__(self, filename=DUMP):
        self.filename = filename
        self.clear()

    def clear(self):
        """Clear dictionaries and load new data."""
        self.packagename2id = {}
        self.content_set_id2pkg_name_ids = {}
        self.content_set_id2label = {}
        self.cpe_id2label = {}
        self.label2cpe_id = {}
        self.content_set_id2cpe_ids = {}
        self.repo_id2cpe_ids = {}
        self.label2content_set_id = {}
        self.id2packagename = {}
        self.updates = {}
        self.updates_index = {}
        self.evr2id = {}
        self.id2evr = {}
        self.arch2id = {}
        self.id2arch = {}
        self.arch_compat = {}
        self.package_details = {}
        self.package_details_modified_index = []
        self.nevra2pkgid = {}
        self.repo_detail = {}
        self.repolabel2ids = {}
        self.repopath2ids = {}
        self.pkgid2repoids = {}
        self.errataid2name = {}
        self.pkgid2errataids = {}
        self.errataid2repoids = {}
        self.cve_detail = {}
        self.pkgerrata2module = {}
        self.modulename2id = {}
        self.modulerequire = {}
        self.dbchange = {}
        self.errata_detail = {}
        self.src_pkg_id2pkg_ids = {}
        self.strings = {}
        self.src_pkg_name_id2cs_ids = {}

    async def reload_async(self):
        """Update data and reload dictionaries asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.reload)

    def reload(self):
        """Update data and reload dictionaries."""
        if self.download():
            self.clear()
            self.load_sqlite(self.filename)
            self.build_indexes()

    def build_indexes(self):
        """Build additional indexes."""
        LOGGER.info("Building 'package_detail.modified' index")
        data = [id for id, _ in self.package_details.items()]
        # pylint: disable=attribute-defined-outside-init
        self.package_details_modified_index = sorted(data, key=lambda id: self.package_details[id][PKG_MODIFIED_ID])
        LOGGER.info("Index 'package_detail.modified' done")

    @staticmethod
    def download():
        """Download new version of data."""
        try:
            with open(DUMP, "wb") as file_handle:
                resp = requests.get(CFG.remote_dump, stream=True, verify=CFG.tls_ca_path)  # pylint: disable=missing-timeout
                while True:
                    chunk = resp.raw.read(DEFAULT_CHUNK_SIZE, decode_content=True)
                    if chunk == b"":
                        break
                    file_handle.write(chunk)
                if resp.status_code == 200:
                    return True
                LOGGER.error("Dump download returned HTTP code: %s", resp.status_code)
        except requests.exceptions.RequestException:
            LOGGER.exception("Dump download failed: ")
        return False

    @staticmethod
    def _sqlite_execute(data, query):
        try:
            return data.execute(query)
        except sqlite3.Error as err:
            # file does not exist or has wrong type
            LOGGER.error("Failed to load data %s: %s", query, err)
            return []

    # pylint: disable=too-many-branches,redefined-builtin,broad-except,invalid-name,too-many-statements
    def _load_sqlite(self, data):

        for (id, arch) in self._sqlite_execute(data, 'select id, arch from arch'):
            self.id2arch[int(id)] = arch
            self.arch2id[arch] = int(id)

        for (src, dst) in self._sqlite_execute(data, 'select from_arch_id, to_arch_id from arch_compat'):
            self.arch_compat.setdefault(src, set()).add(int(dst))

        for (id, string) in self._sqlite_execute(data, 'select id, string from string'):
            self.strings[int(id)] = string

        for (id, label) in self._sqlite_execute(data, 'select id, label from content_set'):
            self.content_set_id2label[id] = label
            self.label2content_set_id[label] = id

        for (id, name) in self._sqlite_execute(data, 'select id, packagename from packagename'):
            self.packagename2id[str(name)] = int(id)
            self.id2packagename[int(id)] = str(name)

        for (cs_id, name_id) in self._sqlite_execute(data,
                                                     "select content_set_id, pkg_name_id from content_set_pkg_name"):
            self.content_set_id2pkg_name_ids.setdefault(cs_id, array.array('q')).append(name_id)

        for (cs_id, src_name_id) in self._sqlite_execute(data,
                                                         "select content_set_id, src_pkg_name_id from content_set_src_pkg_name"):
            self.src_pkg_name_id2cs_ids.setdefault(src_name_id, array.array('q')).append(cs_id)

        for (cpe_id, label) in self._sqlite_execute(data, "select id, label from cpe"):
            self.cpe_id2label[cpe_id] = label
            self.label2cpe_id[label] = cpe_id

        for (cpe_id, cs_id) in self._sqlite_execute(data, "select cpe_id, content_set_id from cpe_content_set"):
            self.content_set_id2cpe_ids.setdefault(cs_id, array.array('q')).append(cpe_id)

        for (cpe_id, repo_id) in self._sqlite_execute(data, "select cpe_id, repo_id from cpe_repo"):
            self.repo_id2cpe_ids.setdefault(repo_id, array.array('q')).append(cpe_id)

        for (name_id, pkg_id) in self._sqlite_execute(data,
                                                      'select name_id, package_id from updates order by name_id, package_order'):
            self.updates.setdefault(int(name_id), []).append(int(pkg_id))

        for (name_id, evr_id, order) in self._sqlite_execute(data,
                                                             'select name_id, evr_id, package_order from updates_index order by name_id, package_order'):
            name_id = int(name_id)
            evr_id = int(evr_id)
            order = int(order)
            self.updates_index.setdefault(name_id, {}).setdefault(evr_id, []).append(order)

        for (id, epoch, ver, rel) in self._sqlite_execute(data, 'select id, epoch, version, release from evr'):
            evr = (str(epoch), str(ver), str(rel))
            self.id2evr[int(id)] = evr
            self.evr2id[evr] = int(id)

        for (id, name_id, evr_id, arch_id, sum_id, descr_id, src_pkg_id, modified_str) in self._sqlite_execute(data,
                                                                                                               'select * from package_detail'):
            detail = array.array('q')
            modified_dt = datetime.datetime.strptime(modified_str, '%Y-%m-%d %H:%M:%S.%f')
            modified_int = int(modified_dt.timestamp())
            detail.fromlist([name_id, evr_id, arch_id, sum_id, descr_id, src_pkg_id or 0, modified_int])
            self.package_details[id] = detail
            self.nevra2pkgid[(name_id, evr_id, arch_id)] = id

            if src_pkg_id:
                self.src_pkg_id2pkg_ids.setdefault(src_pkg_id, array.array('q')).append(id)

        for row in self._sqlite_execute(data, """select id, label, name, url, basearch, releasever,
                                                 product, product_id, revision, last_change, third_party from repo_detail"""):
            id = row[0]
            url = row[3]
            repo = (row[1], row[2], url, row[4], row[5], row[6], row[7],
                    parse_datetime(row[8]), parse_datetime(row[9]), bool(row[10]))
            self.repo_detail[id] = repo
            self.repolabel2ids.setdefault(repo[0], array.array('q')).append(id)

            if url:
                try:
                    repo_path = urlparse(url).path.rstrip('/')
                except ValueError as err:
                    LOGGER.warning("Malformend repository URL for repo %d: %s", id, err)
                else:
                    self.repopath2ids.setdefault(repo_path, array.array('q')).append(id)

        for row in self._sqlite_execute(data, "select pkg_id, repo_id from pkg_repo"):
            self.pkgid2repoids.setdefault(row[0], array.array('q')).append(row[1])

        errataid2cves = {}
        cve2eid = {}
        for row in self._sqlite_execute(data, "select errata_id, cve from errata_cve"):
            errataid2cves.setdefault(row[0], []).append(row[1])
            cve2eid.setdefault(row[1], array.array('q')).append(row[0])

        errataid2pkgid = {}
        for row in self._sqlite_execute(data, "select pkg_id, errata_id from pkg_errata "):
            self.pkgid2errataids.setdefault(row[0], array.array('q')).append(row[1])
            errataid2pkgid.setdefault(row[1], array.array('q')).append(row[0])

        errataid2bzs = {}
        for row in self._sqlite_execute(data, "select errata_id, bugzilla from errata_bugzilla"):
            errataid2bzs.setdefault(row[0], []).append(row[1])

        errataid2refs = {}
        for row in self._sqlite_execute(data, "select errata_id, ref from errata_refs"):
            errataid2refs.setdefault(row[0], []).append(row[1])

        errataidmodulestream2pkgid = {}
        for row in self._sqlite_execute(data, "select pkg_id, errata_id, module_stream_id from errata_modulepkg"):
            self.pkgerrata2module.setdefault((row[0], row[1]), set()).add(row[2])
            errataidmodulestream2pkgid.setdefault((row[1], row[2]), array.array('q')).append(row[0])

        errataid2modules = {}
        for row in self._sqlite_execute(data, """select errata_id, module_name, module_stream_id, module_stream,
                                                 module_version, module_context from errata_module"""):
            if row[0] not in errataid2modules:
                errataid2modules[row[0]] = {}
            if (row[1], row[3], row[4], row[5]) not in errataid2modules[row[0]]:
                errataid2modules[row[0]][(row[1], row[3], row[4], row[5])] = {
                    "module_name": row[1],
                    "module_stream": row[3],
                    "module_version": row[4],
                    "module_context": row[5],
                    "package_list": errataidmodulestream2pkgid.get((row[0], row[2]), array.array('q')),
                    "source_package_list": []  # populated in API
                }
            else:
                # Add packages from module with same name but different architecture, etc.
                errataid2modules[row[0]][(row[1], row[3], row[4], row[5])]["package_list"].extend(
                    errataidmodulestream2pkgid.get((row[0], row[2]), array.array('q'))
                )

        for row in self._sqlite_execute(data, "select * from errata_detail"):
            id = row[0]
            name = row[1]
            errata = (
                row[2], row[3], row[4], row[5], row[6], row[7],
                parse_datetime(row[8]), parse_datetime(row[9]),
                errataid2cves.get(id, []),
                errataid2pkgid.get(id, array.array('q')),
                errataid2bzs.get(id, []),
                errataid2refs.get(id, []),
                list(errataid2modules.get(id, {}).values()),
                row[10], bool(row[11]), bool(row[12]),
                id,
            )
            self.errata_detail[name] = errata
            self.errataid2name[id] = name

        for row in self._sqlite_execute(data, "select errata_id, repo_id from errata_repo"):
            self.errataid2repoids.setdefault(row[0], array.array('q')).append(row[1])

        for row in self._sqlite_execute(data, "select module, stream, stream_id from module_stream"):
            self.modulename2id.setdefault((row[0], row[1]), set()).add(row[2])

        for row in self._sqlite_execute(data, "select stream_id, require_id from module_stream_require"):
            self.modulerequire.setdefault(row[0], set()).add(row[1])

        cveid2cwe = {}
        for row in self._sqlite_execute(data, "select cve_id, cwe from cve_cwe"):
            cveid2cwe.setdefault(row[0], []).append(row[1])

        cveid2pid = {}
        for row in self._sqlite_execute(data, "select cve_id, pkg_id from cve_pkg"):
            cveid2pid.setdefault(row[0], array.array('q')).append(row[1])

        for row in self._sqlite_execute(data, "select * from cve_detail"):
            id = row[0]
            name = row[1]
            item = (
                row[2], row[3], row[4], row[5], row[6],
                parse_datetime(row[7]), parse_datetime(row[8]),
                row[9], row[10],
                cveid2cwe.get(id, []),
                cveid2pid.get(id, array.array('q')),
                cve2eid.get(name, array.array('q')),
                row[11], row[12], row[13]
            )
            self.cve_detail[name] = item

        names = ["exported", "last_change", "repository_changes", "cve_changes", "errata_changes"]

        for row in self._sqlite_execute(data, "select %s from dbchange" % ','.join(names)):
            for (i, v) in enumerate(row):
                self.dbchange[names[i]] = v

    def load_sqlite(self, filename):
        """Load data from sqlite file into dictionaries."""
        # pylint: disable=too-many-branches,too-many-statements
        LOGGER.info("Loading sqlite cache dump...")
        try:
            with sqlite3.connect(filename) as data:
                self._load_sqlite(data)
            LOGGER.info("Loaded dump version: %s", self.dbchange.get('exported', 'unknown'))
        except Exception as err:
            LOGGER.warning("Failed to load data %s: %s", filename, err)
