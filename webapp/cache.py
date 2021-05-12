"""
Module to cache data from file dump.
"""
import array
import asyncio
import dbm
import os
import shelve

from common.config import Config
from common.logging_utils import get_logger

CFG = Config()
DUMP = '/data/vmaas.dbm'
REMOTE_DUMP = CFG.remote_dump

# repo_detail indexes
REPO_LABEL = 0
REPO_NAME = 1
REPO_URL = 2
REPO_BASEARCH = 3
REPO_RELEASEVER = 4
REPO_PRODUCT = 5
REPO_PRODUCT_ID = 6
REPO_REVISION = 7
REPO_THIRD_PARTY = 8

# package detail indexes
PKG_NAME_ID = 0
PKG_EVR_ID = 1
PKG_ARCH_ID = 2
PKG_SUMMARY_ID = 3
PKG_DESC_ID = 4
PKG_SOURCE_PKG_ID = 5

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

LOGGER = get_logger(__name__)


def as_long_arr(data):
    """Make a native i64 array from list of ints"""
    arr = array.array('q')
    arr.fromlist(data)
    return arr


class Cache:
    """ Cache class. """

    # pylint: disable=too-many-instance-attributes
    def __init__(self, filename=DUMP):
        self.filename = filename
        self.clear()
        self.reload()

    def clear(self):
        """Clear dictionaries and load new data."""
        self.packagename2id = {}
        self.content_set_id2pkg_name_ids = {}
        self.content_set_id2label = {}
        self.cpe_id2label = {}
        self.label2cpe_id = {}
        self.content_set_id2cpe_ids = {}
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
        self.nevra2pkgid = {}
        self.repo_detail = {}
        self.repolabel2ids = {}
        self.pkgid2repoids = {}
        self.errataid2name = {}
        self.pkgid2errataids = {}
        self.errataid2repoids = {}
        self.cve_detail = {}
        self.pkgerrata2module = {}
        self.modulename2id = {}
        self.dbchange = {}
        self.errata_detail = {}
        self.src_pkg_id2pkg_ids = {}
        self.strings = {}
        self.src_pkg_name_id2cs_ids = {}
        self.cpe_id2ovaldefinition_ids = {}
        self.packagename_id2definition_ids = {}
        self.ovaldefinition_detail = {}
        self.ovaldefinition_id2cves = {}
        self.ovalcriteria_id2type = {}
        self.ovalcriteria_id2depcriteria_ids = {}
        self.ovalcriteria_id2deptest_ids = {}
        self.ovaltest_detail = {}
        self.ovaltest_id2states = {}
        self.ovalstate_id2arches = {}
    
    def debug(self):
        """Clear dictionaries and load new data."""
        LOGGER.info("packagename2id: %s", len(self.packagename2id))
        LOGGER.info("content_set_id2pkg_name_ids: %s, %s", len(self.content_set_id2pkg_name_ids), sum([len(x) for x in self.content_set_id2pkg_name_ids.values()]))
        LOGGER.info("content_set_id2label: %s", len(self.content_set_id2label))
        LOGGER.info("cpe_id2label: %s", len(self.cpe_id2label))
        LOGGER.info("label2cpe_id: %s", len(self.label2cpe_id))
        LOGGER.info("content_set_id2cpe_ids: %s, %s", len(self.content_set_id2cpe_ids), sum([len(x) for x in self.content_set_id2cpe_ids.values()]))
        LOGGER.info("label2content_set_id: %s", len(self.label2content_set_id))
        LOGGER.info("id2packagename: %s", len(self.id2packagename))
        LOGGER.info("updates: %s, %s", len(self.updates), sum([len(x) for x in self.updates.values()]))
        LOGGER.info("updates_index: %s", len(self.updates_index))
        LOGGER.info("evr2id: %s", len(self.evr2id))
        LOGGER.info("id2evr: %s", len(self.id2evr))
        LOGGER.info("arch2id: %s", len(self.arch2id))
        LOGGER.info("id2arch: %s", len(self.id2arch))
        LOGGER.info("arch_compat: %s", len(self.arch_compat))
        LOGGER.info("package_details: %s", len(self.package_details))
        LOGGER.info("nevra2pkgid: %s", len(self.nevra2pkgid))
        LOGGER.info("repo_detail: %s", len(self.repo_detail))
        LOGGER.info("repolabel2ids: %s, %s", len(self.repolabel2ids), sum([len(x) for x in self.repolabel2ids.values()]))
        LOGGER.info("pkgid2repoids: %s, %s", len(self.pkgid2repoids), sum([len(x) for x in self.pkgid2repoids.values()]))
        LOGGER.info("errataid2name: %s", len(self.errataid2name))
        LOGGER.info("pkgid2errataids: %s, %s", len(self.pkgid2errataids), sum([len(x) for x in self.pkgid2errataids.values()]))
        LOGGER.info("errataid2repoids: %s, %s", len(self.errataid2repoids), sum([len(x) for x in self.errataid2repoids.values()]))
        LOGGER.info("cve_detail: %s", len(self.cve_detail))
        LOGGER.info("pkgerrata2module: %s", len(self.pkgerrata2module))
        LOGGER.info("modulename2id: %s", len(self.modulename2id))
        LOGGER.info("dbchange: %s", len(self.dbchange))
        LOGGER.info("errata_detail: %s", len(self.errata_detail))
        LOGGER.info("src_pkg_id2pkg_ids: %s, %s", len(self.src_pkg_id2pkg_ids), sum([len(x) for x in self.src_pkg_id2pkg_ids.values()]))
        LOGGER.info("strings: %s", len(self.strings))
        LOGGER.info("src_pkg_name_id2cs_ids: %s, %s", len(self.src_pkg_name_id2cs_ids), sum([len(x) for x in self.src_pkg_name_id2cs_ids.values()]))
        LOGGER.info("cpe_id2ovaldefinition_ids: %s, %s", len(self.cpe_id2ovaldefinition_ids), sum([len(x) for x in self.cpe_id2ovaldefinition_ids.values()]))
        LOGGER.info("packagename_id2definition_ids: %s, %s", len(self.packagename_id2definition_ids), sum([len(x) for x in self.packagename_id2definition_ids.values()]))
        LOGGER.info("ovaldefinition_detail: %s", len(self.ovaldefinition_detail))
        LOGGER.info("ovaldefinition_id2cves: %s, %s", len(self.ovaldefinition_id2cves), sum([len(x) for x in self.ovaldefinition_id2cves.values()]))
        LOGGER.info("ovalcriteria_id2type: %s", len(self.ovalcriteria_id2type))
        LOGGER.info("ovalcriteria_id2depcriteria_ids: %s, %s", len(self.ovalcriteria_id2depcriteria_ids), sum([len(x) for x in self.ovalcriteria_id2depcriteria_ids.values()]))
        LOGGER.info("ovalcriteria_id2deptest_ids: %s, %s", len(self.ovalcriteria_id2deptest_ids), sum([len(x) for x in self.ovalcriteria_id2deptest_ids.values()]))
        LOGGER.info("ovaltest_detail: %s", len(self.ovaltest_detail))
        LOGGER.info("ovaltest_id2states: %s, %s", len(self.ovaltest_id2states), sum([len(x) for x in self.ovaltest_id2states.values()]))
        LOGGER.info("ovalstate_id2arches: %s, %s", len(self.ovalstate_id2arches), sum([len(x) for x in self.ovalstate_id2arches.values()]))

    async def reload_async(self):
        """Update data and reload dictionaries asynchronously."""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.reload)

    def reload(self):
        """Update data and reload dictionaries."""
        if self.download():
            self.clear()
            self.load(self.filename)
            self.debug()

    @staticmethod
    def download():
        """Download new version of data."""
        return not os.system("rsync -a --copy-links --quiet %s %s" % (REMOTE_DUMP, DUMP))

    def load(self, filename):
        """Load data from shelve file into dictionaries."""
        # pylint: disable=too-many-branches,too-many-statements
        LOGGER.info("Loading cache dump...")

        try:
            with shelve.open(filename, 'r') as data:
                for item in data:
                    relation, key = item.split(":", 1)
                    if relation == "packagename2id":
                        self.packagename2id[key] = data[item]
                    elif relation == "id2packagename":
                        self.id2packagename[int(key)] = data[item]
                    elif relation == "src_pkg_name_id2cs_ids":
                        self.src_pkg_name_id2cs_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "content_set_id2pkg_name_ids":
                        self.content_set_id2pkg_name_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "content_set_id2label":
                        self.content_set_id2label[int(key)] = data[item]
                    elif relation == "label2content_set_id":
                        self.label2content_set_id[key] = data[item]
                    elif relation == "cpe_id2label":
                        self.cpe_id2label[int(key)] = data[item]
                    elif relation == "label2cpe_id":
                        self.label2cpe_id[key] = data[item]
                    elif relation == "content_set_id2cpe_ids":
                        self.content_set_id2cpe_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "updates":
                        self.updates[int(key)] = data[item]
                    elif relation == "updates_index":
                        self.updates_index[int(key)] = data[item]
                    elif relation == "evr2id":
                        epoch, version, release = key.split(":", 2)
                        self.evr2id[(epoch, version, release)] = data[item]
                    elif relation == "id2evr":
                        self.id2evr[int(key)] = data[item]
                    elif relation == "arch2id":
                        self.arch2id[key] = data[item]
                    elif relation == "id2arch":
                        self.id2arch[int(key)] = data[item]
                    elif relation == "arch_compat":
                        self.arch_compat[int(key)] = data[item]
                    elif relation == "package_details":
                        self.package_details[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "nevra2pkgid":
                        name_id, evr_id, arch_id = key.split(":", 2)
                        self.nevra2pkgid[(int(name_id), int(evr_id), int(arch_id))] = data[item]
                    elif relation == "repo_detail":
                        self.repo_detail[int(key)] = data[item]
                    elif relation == "repolabel2ids":
                        self.repolabel2ids[key] = as_long_arr(list(data[item]))
                    elif relation == "pkgid2repoids":
                        self.pkgid2repoids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "errataid2name":
                        self.errataid2name[int(key)] = data[item]
                    elif relation == "pkgid2errataids":
                        self.pkgid2errataids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "errataid2repoids":
                        self.errataid2repoids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "cve_detail":
                        self.cve_detail[key] = data[item]
                    elif relation == "dbchange":
                        self.dbchange[key] = data[item]
                    elif relation == "errata_detail":
                        self.errata_detail[key] = data[item]
                    elif relation == "pkgerrata2module":
                        pkg_id, errata_id = key.split(":", 1)
                        self.pkgerrata2module[(int(pkg_id), int(errata_id))] = data[item]
                    elif relation == "modulename2id":
                        name, stream_name = key.split(":", 1)
                        self.modulename2id[(name, stream_name)] = data[item]
                    elif relation == "src_pkg_id2pkg_ids":
                        self.src_pkg_id2pkg_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "strings":
                        self.strings[int(key)] = data[item]
                    elif relation == "cpe_id2ovaldefinition_ids":
                        self.cpe_id2ovaldefinition_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "packagename_id2definition_ids":
                        self.packagename_id2definition_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "ovaldefinition_detail":
                        self.ovaldefinition_detail[int(key)] = data[item]
                    elif relation == "ovaldefinition_id2cves":
                        self.ovaldefinition_id2cves[int(key)] = data[item]
                    elif relation == "ovalcriteria_id2type":
                        self.ovalcriteria_id2type[int(key)] = data[item]
                    elif relation == "ovalcriteria_id2depcriteria_ids":
                        self.ovalcriteria_id2depcriteria_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "ovalcriteria_id2deptest_ids":
                        self.ovalcriteria_id2deptest_ids[int(key)] = as_long_arr(list(data[item]))
                    elif relation == "ovaltest_detail":
                        self.ovaltest_detail[int(key)] = data[item]
                    elif relation == "ovaltest_id2states":
                        self.ovaltest_id2states[int(key)] = data[item]
                    elif relation == "ovalstate_id2arches":
                        self.ovalstate_id2arches[int(key)] = data[item]
                    else:
                        LOGGER.warning("Unknown relation in data: %s", relation)

        except dbm.error as err:
            # file does not exist or has wrong type
            LOGGER.warning("Failed to load data %s: %s", filename, err)
            return
        LOGGER.info("Loaded dump version: %s", self.dbchange.get('exported', 'unknown'))
