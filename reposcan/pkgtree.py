#!/usr/bin/python3
"""
Tool for exporting package tree containing CVEs, release date and
channels/streams for use by Product Security.
"""

import glob
import os
import json
from common.logging import get_logger, init_logging
from common.dateutil import format_datetime, now
from database.database_handler import DatabaseHandler, NamedCursor, init_db

KEEP_COPIES = 2
PKGTREE_FILE = '/data/pkg_tree.json'
LOGGER = get_logger(__name__)

# copied from webapp/utils.py
def _join_packagename(name, epoch, version, release, arch):
    """
    Build a package name from the separate NEVRA parts
    """
    epoch = ("%s:" % epoch) if int(epoch) else ''
    return "%s-%s%s-%s.%s" % (name, epoch, version, release, arch)

class JsonPkgTree: # pylint: disable=too-many-instance-attributes
    """Class for creating package tree json file from database."""
    def __init__(self, db_instance, filename):
        self.db_instance = db_instance
        self.filename = filename
        self.outputdata = {}
        self.datadict = {}
        self.pkgnameid2pkgname = {}
        self.evrid2evr = {}
        self.archid2arch = {}
        self.packagedata = {}
        self.repodata = {}
        self.cvename = {}
        self.erratadata = {}

    def _named_cursor(self):
        return NamedCursor(self.db_instance)

    def dump(self):
        """Dump necessary data tu disk file"""
        starttime = now()
        timestamp = format_datetime(starttime)
        dump_filename = '%s-%s' % (self.filename, timestamp)
        self.outputdata['timestamp'] = timestamp
        self.outputdata['packages'] = {}
        LOGGER.info("Loading data")
        self.load_packagenames()
        self.load_evr()
        self.load_arch()
        self.load_repodata()
        self.load_cves()
        self.load_errata()
        self.associate_cves_to_errata()
        self.load_packages()
        self.associate_repos()
        self.associate_errata()
        LOGGER.info("Exporting data to %s", dump_filename)
        with open(dump_filename, 'w') as dump_file:
            json.dump(self.outputdata, dump_file, indent=2, ensure_ascii=False)
        # relink to the latest file
        try:
            os.unlink(self.filename)
        except FileNotFoundError:
            pass
        os.symlink(dump_filename, self.filename)
        LOGGER.info("Finished exporting data.  Elapsed time: %s", now() - starttime)
        # remove old data above limit
        old_data = sorted(glob.glob("%s-*" % self.filename), reverse=True)
        for fname in old_data[KEEP_COPIES:]:
            LOGGER.info("Removing old dump %s", fname)
            os.unlink(fname)

    def load_packagenames(self):
        """Load the datadict and start filling in outputdata"""
        with self._named_cursor() as cursor:
            cursor.execute("""select id, name
                                from package_name order by name
                           """)
            for name_id, pkg_name in cursor:
                self.datadict[name_id] = []
                self.pkgnameid2pkgname[name_id] = pkg_name
                self.outputdata['packages'][pkg_name] = self.datadict[name_id]

    def load_evr(self):
        """Load the evrid2evr dict"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, epoch, version, release from evr")
            for evr_id, epoch, ver, rel in cursor:
                self.evrid2evr[evr_id] = (epoch, ver, rel)

    def load_arch(self):
        """Load the archid2arch dict"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, name from arch")
            for arch_id, name in cursor:
                self.archid2arch[arch_id] = name

    def load_repodata(self):
        """Load the repo data"""
        with self._named_cursor() as cursor:
            cursor.execute("""select r.id,
                                     cs.label,
                                     cs.name,
                                     r.basearch_id,
                                     r.releasever,
                                     r.revision
                                from repo r
                                join content_set cs on cs.id = r.content_set_id
                           """)
            for repo_id, label, name, arch_id, releasever, revision in cursor:
                self.repodata[repo_id] = {'revision': revision,
                                          'data': {'label': label,
                                                   'name': name,
                                                   'arch': self.archid2arch[arch_id],
                                                   'releasever': releasever,
                                                   'revision':format_datetime(revision)}
                                         }

    def load_cves(self):
        """Load CVE data"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, name from cve")
            for cve_id, name in cursor:
                self.cvename[cve_id] = name

    def load_errata(self):
        """Load the errata data"""
        with self._named_cursor() as cursor:
            cursor.execute("select id, name, issued from errata")
            for errata_id, name, issued in cursor:
                self.erratadata[errata_id] = {'issued': issued,
                                              'data': {'name': name,
                                                       'issued': format_datetime(issued)}
                                             }

    def associate_cves_to_errata(self):
        """Associate CVEs to errata"""
        with self._named_cursor() as cursor:
            cursor.execute("select errata_id, cve_id from errata_cve")
            for errata_id, cve_id in cursor:
                self.erratadata[errata_id]['data'].setdefault('cve_list', []).append(self.cvename[cve_id])

    def load_packages(self):
        """Load the packages info"""
        with self._named_cursor() as cursor:
            cursor.execute("""select p.id, p.name_id, p.evr_id, p.arch_id
                                from package p
                          inner join evr on p.evr_id = evr.id
                            order by evr.evr""")
            for pkg_id, name_id, evr_id, arch_id in cursor:
                self.add_package_entry(pkg_id, name_id, evr_id, arch_id)


    def add_package_entry(self, pkg_id, name_id, evr_id, arch_id):
        """Add package to the ultimate response"""
        if name_id not in self.pkgnameid2pkgname:
            LOGGER.error("INCONSISTENT DATA: pkg id %s - package name id %s not found", pkg_id, name_id)
        if evr_id not in self.evrid2evr:
            LOGGER.error("INCONSISTEN DATA: pkg id %s - evr id %s not found", pkg_id, evr_id)
        if arch_id not in self.archid2arch:
            LOGGER.error("INCONSISTENT DATA: pkg id %s - arch id %s not found", pkg_id, arch_id)
        (epoch, ver, rel) = self.evrid2evr[evr_id]
        package_nevra = _join_packagename(self.pkgnameid2pkgname[name_id], epoch, ver, rel, self.archid2arch[arch_id])
        self.packagedata[pkg_id] = {'data': {'nevra': package_nevra,
                                             'repositories':[]}
                                   }
        self.datadict[name_id].append(self.packagedata[pkg_id]['data'])

    def associate_repos(self):
        """Add repodata to the package entries"""
        with self._named_cursor() as cursor:
            cursor.execute("select pkg_id, repo_id from pkg_repo")
            for pkg_id, repo_id in cursor:
                self.packagedata[pkg_id]['data']['repositories'].append(self.repodata[repo_id]['data'])

    def associate_errata(self):
        """Add errata data to the package entries"""
        with self._named_cursor() as cursor:
            cursor.execute("select pkg_id, errata_id from pkg_errata")
            for pkg_id, errata_id in cursor:
                edata = self.erratadata[errata_id]
                if edata['issued']:
                    if 'first_published' not in self.packagedata[pkg_id] or \
                       edata['issued'] < self.packagedata[pkg_id]['first_published']:
                        self.packagedata[pkg_id]['first_published'] = edata['issued']
                        self.packagedata[pkg_id]['data']['first_published'] = edata['data']['issued']
                self.packagedata[pkg_id]['data'].setdefault('errata', []).append(edata['data'])


def main(filename):
    """ Main loop."""
    init_logging()
    init_db()
    db_instance = DatabaseHandler.get_connection()
    data = JsonPkgTree(db_instance, filename)
    data.dump()

if __name__ == '__main__':
    main(PKGTREE_FILE)
