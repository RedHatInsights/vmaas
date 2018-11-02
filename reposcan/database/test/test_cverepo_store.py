"""Unit test for cverepo_store."""
# pylint: disable=unused-argument, attribute-defined-outside-init

from decimal import Decimal

import pytest

from database.cverepo_store import CveRepoStore
from database.test.db_idxs import (
    CVE_CVSS3_METRIC,
    CVE_CVSS3_SCORE,
    CVE_DESCRIPTION,
    CVE_IMPACT_ID,
    CVE_NAME,
    CVE_PUBLISHED,
    CVE_SECONDARY_URL,
)
from nistcve.cvejson import CveJson
from nistcve.cvemeta import CveMeta
from nistcve.cverepo import CveRepo


class TestCveRepoStore:
    """TestCveRepoStore class. Test nistcve repo store."""

    @pytest.fixture
    def repo_obj(self):
        """Setup CveRepo obj."""
        self.cverepo = CveRepo("unittest")
        self.cverepo.json = CveJson("test_data/nistcve/nvdcve-1.0-modified.json")
        self.cverepo.meta = CveMeta("test_data/nistcve/nvdcve-1.0-modified.meta")

    def test_store(self, db_conn, repo_obj):
        """Test nistcve repo store."""
        repo_store = CveRepoStore()
        repo_store.store(self.cverepo)
        cur = db_conn.cursor()
        cur.execute("select * from cve where name = 'CVE-2009-1437'")
        cve = cur.fetchone()
        assert cve[CVE_NAME] == "CVE-2009-1437"
        assert "CoolPlayer" in cve[CVE_DESCRIPTION]
        assert cve[CVE_IMPACT_ID] == 6
        assert cve[CVE_PUBLISHED].year == 2009
        assert cve[CVE_SECONDARY_URL] == "http://osvdb.org/53885"

        cur.execute("select * from cve where name = 'CVE-2011-2902'")
        cve = cur.fetchone()
        assert cve[CVE_NAME] == "CVE-2011-2902"
        assert "xpdf" in cve[CVE_DESCRIPTION]
        assert cve[CVE_PUBLISHED].year == 2018
        assert cve[CVE_IMPACT_ID] == 3
        assert cve[CVE_CVSS3_SCORE] == Decimal("5.3")
        assert cve[CVE_CVSS3_METRIC] == "CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N"
        assert cve[CVE_SECONDARY_URL] == "http://www.openwall.com/lists/oss-security/2014/02/08/5"
