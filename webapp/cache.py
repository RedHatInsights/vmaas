"""
Module to cache data from file dump.
"""

import dbm
import os
import shelve

DUMP = '/data/vmaas.dbm'
REMOTE_DUMP = 'rsync://reposcan/data/vmaas.dbm'

# repo_detail indexes
REPO_LABEL = 0
REPO_NAME = 1
REPO_URL = 2
REPO_BASEARCH = 3
REPO_RELEASEVER = 4
REPO_PRODUCT = 5
REPO_PRODUCT_ID = 6
REPO_REVISION = 7

class Cache(object):
    """ Cache class. """
    # pylint: disable=too-many-instance-attributes
    def __init__(self, filename=DUMP):
        self.filename = filename
        self.packagename2id = {}
        self.id2packagename = {}
        self.updates = {}
        self.updates_index = {}
        self.evr2id = {}
        self.id2evr = {}
        self.arch2id = {}
        self.id2arch = {}
        self.arch_compat = {}
        self.package_details = {}
        self.repo_detail = {}
        self.repolabel2ids = {}
        self.productid2repoids = {}
        self.pkgid2repoids = {}
        self.errataid2name = {}
        self.pkgid2errataids = {}
        self.errataid2repoids = {}
        self.reload()

    def clear(self):
        """Clear dictionaries and load new data."""
        self.packagename2id = {}
        self.id2packagename = {}
        self.updates = {}
        self.updates_index = {}
        self.evr2id = {}
        self.id2evr = {}
        self.arch2id = {}
        self.id2arch = {}
        self.arch_compat = {}
        self.package_details = {}
        self.repo_detail = {}
        self.repolabel2ids = {}
        self.productid2repoids = {}
        self.pkgid2repoids = {}
        self.errataid2name = {}
        self.pkgid2errataids = {}
        self.errataid2repoids = {}

    def reload(self):
        """Update data and reload dictionaries."""
        if self.download():
            self.clear()
            self.load(self.filename)

    @staticmethod
    def download():
        """Download new version of data."""
        return not os.system("rsync -a --quiet %s %s" % (REMOTE_DUMP, DUMP))

    def load(self, filename):
        """Load data from shelve file into dictionaries."""
        # pylint: disable=too-many-branches
        try:
            data = shelve.open(filename, 'r')
        except dbm.error:
            # file does not exist or has wrong type
            return
        for item in data:
            relation, key = item.split(":", 1)
            if relation == "packagename2id":
                self.packagename2id[key] = data[item]
            elif relation == "id2packagename":
                self.id2packagename[int(key)] = data[item]
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
                self.package_details[int(key)] = data[item]
            elif relation == "repo_detail":
                self.repo_detail[int(key)] = data[item]
            elif relation == "repolabel2ids":
                self.repolabel2ids[key] = data[item]
            elif relation == "productid2repoids":
                self.productid2repoids[int(key)] = data[item]
            elif relation == "pkgid2repoids":
                self.pkgid2repoids[int(key)] = data[item]
            elif relation == "errataid2name":
                self.errataid2name[int(key)] = data[item]
            elif relation == "pkgid2errataids":
                self.pkgid2errataids[int(key)] = data[item]
            elif relation == "errataid2repoids":
                self.errataid2repoids[int(key)] = data[item]
            else:
                raise KeyError("Unknown relation in data: %s" % relation)
