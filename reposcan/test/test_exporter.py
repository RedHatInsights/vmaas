"""
Unit test classes for exporter module.
"""
# pylint: disable=no-self-use

import shelve

from common.dateutil import parse_datetime
from exporter import DataDump

TEST_DUMP_FILE = "/tmp/dump.output"

class TestExporter:
    """Test Exporter class."""

    def test_dump(self, exporter_db_conn):
        """Test database dump."""
        ddump = DataDump(exporter_db_conn, TEST_DUMP_FILE)
        ddump.dump()
        with shelve.open(TEST_DUMP_FILE) as dbdump:
            # from IPython import embed; embed()

            self.check_predefined_content(dbdump)
            self.check_packagename(dbdump)
            self.check_updates(dbdump)
            self.check_evr(dbdump)
            self.check_package_details(dbdump)
            self.check_repo(dbdump)
            self.check_errata(dbdump)
            self.check_modules(dbdump)

    def check_predefined_content(self, dbdump):
        """Check the predefined database content"""
        arch_list = ["noarch", "i386", "i486", "i586", "i686", "alpha", "alphaev6", "ia64",
                     "sparc", "sparcv9", "sparc64", "s390", "athlon", "s390x", "ppc",
                     "ppc64le", "pSeries", "iSeries", "x86_64", "ppc64iseries",
                     "ppc64pseries", "ia32e", "amd64", "aarch64", "armv7hnl",
                     "armv7hl", "armv7l", "armv6hl", "armv6l", "armv5tel"]
        for arch in arch_list:
            archkey = "arch2id:%s" % arch
            assert archkey in dbdump
            idkey = "id2arch:%d" % dbdump[archkey]
            assert idkey in dbdump
            assert dbdump[idkey] == arch

    def check_packagename(self, dbdump):
        """Check packagename dump.  Only packages that received security update."""
        assert "packagename2id:pkg-sec-errata1" in dbdump
        assert dbdump["packagename2id:pkg-sec-errata1"] == 101
        assert "id2packagename:101" in dbdump
        assert dbdump["id2packagename:101"] == "pkg-sec-errata1"
        assert "packagename2id:pkg-no-sec-errata2" not in dbdump
        assert "id2packagename:102" not in dbdump
        assert "packagename2id:pkg-errata-cve3" in dbdump
        assert dbdump["packagename2id:pkg-errata-cve3"] == 103
        assert "id2packagename:103" in dbdump
        assert dbdump["id2packagename:103"] == "pkg-errata-cve3"
        assert "packagename2id:pkg-sec-errata4" in dbdump
        assert dbdump["packagename2id:pkg-sec-errata4"] == 104
        assert "id2packagename:104" in dbdump
        assert dbdump["id2packagename:104"] == "pkg-sec-errata4"

    def check_updates(self, dbdump):
        """Check updates in dump."""
        assert "updates:101" in dbdump
        updates1 = dbdump["updates:101"]
        assert updates1 == [301, 302, 303]

        assert "updates:102" not in dbdump

        assert "updates:103" in dbdump
        updates3 = dbdump["updates:103"]
        assert updates3 == [305, 306]

    def check_evr(self, dbdump):
        """Check evr in dump."""
        assert "evr2id:1:1:1" in dbdump
        assert dbdump["evr2id:1:1:1"] == 201
        assert "evr2id:1:1:2" in dbdump
        assert dbdump["evr2id:1:1:2"] == 202
        assert "evr2id:1:1:2" in dbdump
        assert dbdump["evr2id:1:1:3"] == 203
        assert "evr2id:2:2:2" in dbdump
        assert dbdump["evr2id:2:2:2"] == 204
        assert "evr2id:3:3:3" in dbdump
        assert dbdump["evr2id:3:3:3"] == 205
        assert "evr2id:4:4:4" in dbdump
        assert dbdump["evr2id:4:4:4"] == 206

        assert "id2evr:201" in dbdump
        assert dbdump["id2evr:201"] == ("1", "1", "1")

    def check_package_details(self, dbdump):
        """Check package details in dump."""
        assert "package_details:301" in dbdump
        assert dbdump["package_details:301"] == (101, 201, 1, 1, "summary1", "description1")

    def check_repo(self, dbdump):
        """Check repo data in dump."""
        assert "repo_detail:801" in dbdump
        assert dbdump["repo_detail:801"][0] == "content set 1"
        assert dbdump["repo_detail:801"][1] == "content-set-name-1"
        assert dbdump["repo_detail:801"][2] == "https://www.repourl.com/repo1"
        assert dbdump["repo_detail:801"][3] == "noarch"
        assert dbdump["repo_detail:801"][4] == "1"
        assert dbdump["repo_detail:801"][5] == "product1"
        assert dbdump["repo_detail:801"][6] == 501
        assert parse_datetime(dbdump["repo_detail:801"][7]) == parse_datetime("2019-08-01T01:00:00-05:00")
        #assert dbdump["repo_detail:801"] == ("content set 1", "content-set-name-1",
        #                                   "https://www.repourl.com/repo1", "noarch", "1",
        #                                   "product1", 501, "2019-08-01T01:00:00-05:00")
        assert "repolabel2ids:content set 1" in dbdump
        assert dbdump["repolabel2ids:content set 1"] == [801]

        assert "pkgid2repoids:301" in dbdump
        assert "pkgid2repoids:302" in dbdump
        assert "pkgid2repoids:303" in dbdump
        assert "pkgid2repoids:304" not in dbdump
        assert "pkgid2repoids:305" in dbdump
        assert "pkgid2repoids:306" in dbdump
        repo_list = dbdump["pkgid2repoids:306"]
        assert 801 in repo_list
        assert 802 in repo_list
        assert "pkgid2repoids:307" in dbdump

    def check_errata(self, dbdump):
        """Check errata in dump."""
        assert "errataid2name:401" in dbdump
        assert dbdump["errataid2name:401"] == "errata1"
        assert "errataid2name:402" not in dbdump
        assert "errataid2name:403" in dbdump
        assert dbdump["errataid2name:403"] == "errata3"

        assert "pkgid2errataids:301" in dbdump
        assert 401 in dbdump["pkgid2errataids:301"]
        assert 403 in dbdump["pkgid2errataids:301"]
        assert "pkgid2errataids:302" in dbdump
        assert 401 in dbdump["pkgid2errataids:302"]
        assert "pkgid2errataids:303" not in dbdump

        assert "errataid2repoids:401" in dbdump
        assert 801 in dbdump["errataid2repoids:401"]
        assert 802 in dbdump["errataid2repoids:401"]
        assert "errataid2repoids:402" not in dbdump
        assert "errataid2repoids:403" in dbdump
        assert 801 in dbdump["errataid2repoids:403"]

    def check_modules(self, dbdump):
        """Check modules in dump."""
        assert "pkgerrata2module:301:401" in dbdump
        assert 1101 in dbdump["pkgerrata2module:301:401"]
        assert "pkgerrata2module:302:401" in dbdump
        assert 1103 in dbdump["pkgerrata2module:302:401"]
        assert "pkgerrata2module:307:401" in dbdump
        assert 1102 in dbdump["pkgerrata2module:307:401"]

        assert "modulename2id:module1:stream1" in dbdump
        assert 1101 in dbdump["modulename2id:module1:stream1"]
        assert 1103 in dbdump["modulename2id:module1:stream1"]
        assert "modulename2id:module2:stream2" in dbdump
        assert 1102 in dbdump["modulename2id:module2:stream2"]
