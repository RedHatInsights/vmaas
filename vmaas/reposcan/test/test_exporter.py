"""
Unit test classes for exporter module.
"""
# pylint: disable=no-self-use

import time
import sqlite3

from vmaas.common.date_utils import parse_datetime
from vmaas.reposcan.exporter import SqliteDump
from vmaas.reposcan.conftest import write_testing_data

TEST_DUMP_FILE = "./dump.output"


class TestExporter:
    """Test Exporter class."""

    def test_dump(self, db_conn):
        """Test database dump."""
        write_testing_data(db_conn)
        sqlite_dump = SqliteDump(db_conn, TEST_DUMP_FILE)
        sqlite_dump.dump(time.time())
        with sqlite3.connect(TEST_DUMP_FILE) as dbdump:
            # from IPython import embed; embed()

            self.check_predefined_content(dbdump)
            self.check_packagename(dbdump)
            self.check_updates(dbdump)
            self.check_evr(dbdump)
            self.check_package_details(dbdump)
            self.check_repo(dbdump)
            self.check_errata(dbdump)
            self.check_modules(dbdump)
            self.check_src_pkg_id(dbdump)

    def check_predefined_content(self, dbdump):
        """Check the predefined database content"""
        arch_list = ["noarch", "i386", "i486", "i586", "i686", "alpha", "alphaev6", "ia64",
                     "sparc", "sparcv9", "sparc64", "s390", "athlon", "s390x", "ppc",
                     "ppc64le", "pSeries", "iSeries", "x86_64", "ppc64iseries",
                     "ppc64pseries", "ia32e", "amd64", "aarch64", "armv7hnl",
                     "armv7hl", "armv7l", "armv6hl", "armv6l", "armv5tel"]
        id2arch = {}
        arch2id = {}
        for (arch_id, arch) in dbdump.execute('select id, arch from arch'):
            id2arch[arch_id] = arch
            arch2id[arch] = arch_id

        for arch in arch_list:
            assert arch in arch2id
            assert arch2id[arch] in id2arch
            assert id2arch[arch2id[arch]] == arch

    def check_packagename(self, dbdump):
        """Check packagename dump."""
        id2packagename = {}
        packagename2id = {}
        for (pn_id, packagename) in dbdump.execute('select id, packagename from packagename'):
            id2packagename[pn_id] = packagename
            packagename2id[packagename] = pn_id

        assert "pkg-sec-errata1" in packagename2id
        assert packagename2id["pkg-sec-errata1"] == 101
        assert 101 in id2packagename
        assert id2packagename[101] == "pkg-sec-errata1"
        assert "pkg-no-sec-errata2" in packagename2id
        assert 102 in id2packagename
        assert "pkg-errata-cve3" in packagename2id
        assert packagename2id["pkg-errata-cve3"] == 103
        assert 103 in id2packagename
        assert id2packagename[103] == "pkg-errata-cve3"
        assert "pkg-sec-errata4" in packagename2id
        assert packagename2id["pkg-sec-errata4"] == 104
        assert 104 in id2packagename
        assert id2packagename[104] == "pkg-sec-errata4"

    def check_updates(self, dbdump):
        """Check updates in dump."""
        updates = {}
        for (name_id, pkg_id) in dbdump.execute(
                'select name_id, package_id from updates order by name_id, package_order'):
            updates.setdefault(int(name_id), []).append(int(pkg_id))

        assert 101 in updates
        updates1 = updates[101]
        assert updates1 == [301, 302, 303]

        assert 102 in updates

        assert 103 in updates
        updates3 = updates[103]
        assert updates3 == [305, 306]

    def check_evr(self, dbdump):
        """Check evr in dump."""
        id2evr = {}
        evr2id = {}
        for (evr_id, epoch, ver, rel) in dbdump.execute('select id, epoch, version, release from evr'):
            evr = (str(epoch), str(ver), str(rel))
            id2evr[int(evr_id)] = evr
            evr2id[evr] = int(evr_id)

        assert ("1", "1", "1") in evr2id
        assert evr2id[("1", "1", "1")] == 201
        assert ("1", "1", "2") in evr2id
        assert evr2id[("1", "1", "2")] == 202
        assert ("1", "1", "3") in evr2id
        assert evr2id[("1", "1", "3")] == 203
        assert ("2", "2", "2") in evr2id
        assert evr2id[("2", "2", "2")] == 204
        assert ("3", "3", "3") in evr2id
        assert evr2id[("3", "3", "3")] == 205
        assert ("4", "4", "4") in evr2id
        assert evr2id[("4", "4", "4")] == 206

        assert 201 in id2evr
        assert id2evr[201] == ("1", "1", "1")

    def check_package_details(self, dbdump):
        """Check package details in dump."""
        package_details = {}
        strings = {}
        for (pkg_id, name_id, evr_id, arch_id, sum_id, descr_id, src_pkg_id, modified) in dbdump.execute(
                'select * from package_detail'):
            detail = (name_id, evr_id, arch_id, sum_id, descr_id, src_pkg_id or 0, modified)
            package_details[pkg_id] = detail
        for (str_id, string) in dbdump.execute('select id, string from string'):
            strings[int(str_id)] = string

        assert 301 in package_details
        item = package_details[301]
        assert item[0] == 101
        assert item[1] == 201
        assert item[2] == 1
        assert strings[item[3]] == "summary1"
        assert strings[item[4]] == "description1"
        assert not item[5]
        assert item[6][0:10] == time.strftime('%Y-%m-%d')

    def check_repo(self, dbdump):
        """Check repo data in dump."""
        repo_detail = {}
        repolabel2ids = {}
        pkgid2repoids = {}
        for row in dbdump.execute("select * from repo_detail"):
            repo_id = row[0]
            repo = (row[1], row[2], row[3], row[4], row[5], row[6], row[7],
                    parse_datetime(row[8]), bool(row[9]))
            repo_detail[repo_id] = repo
            repolabel2ids.setdefault(repo[0], []).append(repo_id)
        for row in dbdump.execute("select pkg_id, repo_id from pkg_repo"):
            pkgid2repoids.setdefault(row[0], []).append(row[1])

        assert 801 in repo_detail
        assert repo_detail[801][0] == "content set 1"
        assert repo_detail[801][1] == "content-set-name-1"
        assert repo_detail[801][2] == "https://www.repourl.com/repo1"
        assert repo_detail[801][3] == "noarch"
        assert repo_detail[801][4] == "1"
        assert repo_detail[801][5] == "product1"
        assert repo_detail[801][6] == 501
        assert repo_detail[801][7] == parse_datetime("2019-08-01T01:00:00-05:00")

        assert "content set 1" in repolabel2ids
        assert repolabel2ids["content set 1"] == [801]

        assert 301 in pkgid2repoids
        assert 302 in pkgid2repoids
        assert 303 in pkgid2repoids
        assert 304 in pkgid2repoids
        assert 305 in pkgid2repoids
        assert 306 in pkgid2repoids
        repo_list = pkgid2repoids[306]
        assert 801 in repo_list
        assert 802 in repo_list
        assert 307 in pkgid2repoids

    def check_errata(self, dbdump):
        """Check errata in dump."""
        errataid2name = {}
        pkgid2errataids = {}
        errataid2repoids = {}
        for row in dbdump.execute("select * from errata_detail"):
            errataid2name[row[0]] = row[1]
        for row in dbdump.execute("select pkg_id, errata_id from pkg_errata "):
            pkgid2errataids.setdefault(row[0], []).append(row[1])
        for row in dbdump.execute("select errata_id, repo_id from errata_repo"):
            errataid2repoids.setdefault(row[0], []).append(row[1])

        assert 401 in errataid2name
        assert errataid2name[401] == "errata1"
        assert 402 in errataid2name
        assert 403 in errataid2name
        assert errataid2name[403] == "errata3"

        assert 301 in pkgid2errataids
        assert 401 in pkgid2errataids[301]
        assert 403 in pkgid2errataids[301]
        assert 302 in pkgid2errataids
        assert 401 in pkgid2errataids[302]
        assert 303 not in pkgid2errataids

        assert 401 in errataid2repoids
        assert 801 in errataid2repoids[401]
        assert 802 in errataid2repoids[401]
        assert 402 in errataid2repoids
        assert 403 in errataid2repoids
        assert 801 in errataid2repoids[403]

    def check_modules(self, dbdump):
        """Check modules in dump."""
        pkgerrata2module = {}
        modulename2id = {}
        modulerequire = []
        for row in dbdump.execute("select pkg_id, errata_id, module_stream_id from errata_modulepkg"):
            pkgerrata2module.setdefault((row[0], row[1]), set()).add(row[2])
        for row in dbdump.execute("select module, stream, stream_id from module_stream"):
            modulename2id.setdefault((row[0], row[1]), set()).add(row[2])
        for row in dbdump.execute("select stream_id, require_id from module_stream_require"):
            modulerequire.append(row)

        assert (301, 401) in pkgerrata2module
        assert 1101 in pkgerrata2module[(301, 401)]
        assert (302, 401) in pkgerrata2module
        assert 1103 in pkgerrata2module[(302, 401)]
        assert (307, 401) in pkgerrata2module
        assert 1102 in pkgerrata2module[(307, 401)]
        assert (1102, 1103) in modulerequire

        assert ("module1", "stream1") in modulename2id
        assert 1101 in modulename2id[("module1", "stream1")]
        assert 1103 in modulename2id[("module1", "stream1")]
        assert ("module2", "stream2") in modulename2id
        assert 1102 in modulename2id[("module2", "stream2")]

    def check_src_pkg_id(self, dbdump):
        """Check source package to binary packages
        mapping in dump."""
        src_pkg_id2pkg_ids = {}
        for (pkg_id, _, _, _, _, _, src_pkg_id, _) in dbdump.execute('select * from package_detail'):
            if src_pkg_id:
                src_pkg_id2pkg_ids.setdefault(src_pkg_id, []).append(pkg_id)
        assert len(src_pkg_id2pkg_ids[301]) == 3
        assert set(src_pkg_id2pkg_ids[301]) == {303, 304, 305}
        assert len(src_pkg_id2pkg_ids[302]) == 2
        assert set(src_pkg_id2pkg_ids[302]) == {306, 307}
