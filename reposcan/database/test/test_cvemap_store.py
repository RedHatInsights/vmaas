"""Module for testing cvemap_store."""
# pylint: disable=unused-argument, attribute-defined-outside-init, protected-access

from datetime import datetime
from decimal import Decimal

import pytest

from database.cvemap_store import CvemapStore
from database.test.db_idxs import (
    CVE_CVSS3_METRIC,
    CVE_CVSS3_SCORE,
    CVE_DESCRIPTION,
    CVE_IMPACT_ID,
    CVE_NAME,
    CVE_PUBLISHED,
)
from redhatcve.cvemap_controller import CvemapController


class TestCvemapStore:
    """TestCvemapStore class. Test redhat cve repo store."""

    @pytest.fixture
    def cvemap_obj(self):
        """Setup CvemapStore obj."""
        self.controller = CvemapController()
        self.controller.lastmodified = datetime.utcnow()
        self.controller.tmp_directory = "test_data/cvemap"
        self.cvemap = self.controller._load_xml(self.controller.lastmodified)

        self.cvemap_store = CvemapStore()

    def test_store(self, db_conn, cvemap_obj):
        """Test redhat cvemap store."""
        # store cvemap in DB
        self.cvemap_store.store(self.cvemap)
        cur = db_conn.cursor()
        cur.execute("select * from cve where name = 'CVE-2018-1097'")
        cve = cur.fetchone()
        assert cve[CVE_NAME] == "CVE-2018-1097"
        assert "foreman" in cve[CVE_DESCRIPTION]
        assert cve[CVE_IMPACT_ID] == 4
        assert cve[CVE_PUBLISHED].year == 2018
        assert cve[CVE_CVSS3_SCORE] == Decimal("7.7")
        assert cve[CVE_CVSS3_METRIC] == "CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N"
        # assert cve[0][REDHAT_URL] == "https://access.redhat.com/security/cve/cve-2018-1097"
