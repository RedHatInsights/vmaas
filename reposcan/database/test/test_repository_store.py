"""Test storing repository in DB."""
# pylint: disable=unused-argument, attribute-defined-outside-init, no-self-use

from datetime import datetime

import pytest

from common import utc
from database.product_store import ProductStore
from database.repository_store import RepositoryStore
from database.test.db_idxs import (
    ARCH_NAME,
    CS_LABEL,
    CS_NAME,
    CS_PRODUCT_ID,
    PRODUCT_NAME,
    PRODUCT_RH_ID,
    REPO_BASEARCH_ID,
    REPO_CS_ID,
    REPO_RELEASEVER,
    REPO_URL,
)
from repodata.primary import PrimaryMD
from repodata.primary_db import PrimaryDatabaseMD
from repodata.repository import Repository
from repodata.updateinfo import UpdateInfoMD

PRIMARY_DB = PrimaryDatabaseMD("test_data/repodata/primary_db.sqlite")
PRIMARY = PrimaryMD("test_data/repodata/primary.xml")
UPDATEINFO = UpdateInfoMD("test_data/repodata/updateinfo.xml")
PRODUCTS = {"product": {"product_id": 9, "content_sets": {"cs_label": "cs_name"}}}

REPOSITORY = Repository("repo_url1", "cs_label", "x86_64", "27")
REPOSITORY.primary = PRIMARY_DB
REPOSITORY.updateinfo = UPDATEINFO
REPOSITORY_WITHOUT_UPDATEINFO = Repository("repo_url2", "cs_label", "i386", "27")
REPOSITORY_WITHOUT_UPDATEINFO.primary = PRIMARY_DB
REPOSITORY_PRIMARY_XML = Repository("repo_url3", "cs_label", "ppc64le", "27")
REPOSITORY_PRIMARY_XML.primary = PRIMARY
REPOSITORY_PRIMARY_XML.updateinfo = UPDATEINFO

REPOSITORIES = [
    ("primary_db", REPOSITORY),
    ("primary_xml", REPOSITORY_PRIMARY_XML),
    ("without updateinfo", REPOSITORY_WITHOUT_UPDATEINFO),
]


class TestRepositoryStore:
    """TestRepositoryStore class. Test repository store"""

    @pytest.fixture
    def repo_setup(self):
        """Setup repo_store object."""
        product_store = ProductStore()
        product_store.store(PRODUCTS)

        self.repo_store = RepositoryStore()

    @pytest.mark.first
    @pytest.mark.parametrize("repository", REPOSITORIES, ids=[r[0] for r in REPOSITORIES])
    def test_repo_store(self, db_conn, repo_setup, repository):
        """Test storing repository data in DB."""

        # update with updated = None result in IntegrityError
        if repository[1].updateinfo:
            for update in repository[1].updateinfo.updates:
                if update["updated"] is None:
                    update["updated"] = datetime.now(utc.UTC)

        # store repository
        self.repo_store.store(repository[1])

        cur = db_conn.cursor()
        cur.execute("select * from repo where url = '{}'".format(repository[1].repo_url))
        repo = cur.fetchone()
        cur.execute("select * from content_set where id = {}".format(repo[REPO_CS_ID]))
        content_set = cur.fetchone()
        cur.execute("select * from product where id = {}".format(content_set[CS_PRODUCT_ID]))
        product = cur.fetchone()
        cur.execute("select * from arch where id = {}".format(repo[REPO_BASEARCH_ID]))
        arch = cur.fetchone()

        assert repo[REPO_URL] == repository[1].repo_url
        assert repo[REPO_RELEASEVER] == repository[1].releasever

        assert content_set[CS_LABEL] == "cs_label"
        assert content_set[CS_NAME] == "cs_name"

        assert product[PRODUCT_NAME] == "product"
        assert product[PRODUCT_RH_ID] == 9

        assert arch[ARCH_NAME] == repository[1].basearch

    @pytest.mark.parametrize("repository", REPOSITORIES, ids=[r[0] for r in REPOSITORIES])
    def test_repo_pkgs(self, db_conn, repository):
        """Test that packages from repo are present in DB."""
        cur = db_conn.cursor()
        cur.execute("select id from repo where url = '{}'".format(repository[1].repo_url))
        repo_id = cur.fetchone()[0]
        cur.execute("select count(*) from pkg_repo where repo_id = {}".format(repo_id))
        pkg_num = cur.fetchone()[0]

        assert pkg_num == 12  # 12 packages expected from primary.xml/primary.db

    @pytest.mark.parametrize("repository", REPOSITORIES, ids=[r[0] for r in REPOSITORIES])
    def test_repo_errata(self, db_conn, repository):
        """Test that errata from repo are present in DB."""
        cur = db_conn.cursor()
        cur.execute("select id from repo where url = '{}'".format(repository[1].repo_url))
        repo_id = cur.fetchone()[0]
        cur.execute("select count(*) from errata_repo where repo_id = {}".format(repo_id))
        errata_num = cur.fetchone()[0]

        # only repository with updateifo has errata
        if repository[1].updateinfo:
            assert errata_num == 9  # 9 erata expected from primary.xml/primary.db
        else:
            assert errata_num == 0

    @pytest.mark.parametrize("repository", REPOSITORIES, ids=[r[0] for r in REPOSITORIES])
    def test_pkgs_count(self, db_conn, repository):
        """Test all packages count in package table."""
        cur = db_conn.cursor()
        cur.execute("select count(*) from package")
        pkg_num = cur.fetchone()[0]

        assert pkg_num == 18  # 18 packages expected from primary.xml/primary.db

    @pytest.mark.parametrize("repository", REPOSITORIES, ids=[r[0] for r in REPOSITORIES])
    def test_rpm_pkgs_count(self, db_conn, repository):
        """Test rpm packages count in package table."""
        cur = db_conn.cursor()
        cur.execute("select count(*) from package where source_package_id is not null")
        pkg_num = cur.fetchone()[0]

        assert pkg_num == 12

    @pytest.mark.parametrize("repository", REPOSITORIES, ids=[r[0] for r in REPOSITORIES])
    def test_srpm_pkgs_count(self, db_conn, repository):
        """Test srpm packages count in package table."""
        cur = db_conn.cursor()
        cur.execute("select count(*) from package where source_package_id is null")
        pkg_num = cur.fetchone()[0]

        assert pkg_num == 6

    def test_pkg_errata_count(self, db_conn):
        """Test that package - errata association are stored."""
        cur = db_conn.cursor()
        cur.execute("select count(*) from pkg_errata")
        cnt = cur.fetchone()[0]

        assert cnt == 9
