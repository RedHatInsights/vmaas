"""
Unit test classes for repository controller module.
"""

import os
import shutil

from vmaas.reposcan.repodata.repository_controller import RepositoryController

from vmaas.reposcan.database import product_store
from vmaas.reposcan.download.downloader import DownloadItem, FileDownloadThread
from vmaas.reposcan.conftest import reset_db, write_testing_data
from vmaas.reposcan.database.database_handler import DatabaseHandler
from vmaas.reposcan.reposcan import DEFAULT_ORG_NAME


def download_mock(self, download_item: DownloadItem):
    """Mock downloading function with copying from
    testing data directory."""
    src = download_item.source_url.split("/")[-1]
    src_path = "test_data/repodata/integration/" + src
    if src.endswith(".gz"):  # prepare archive file
        base = src[:-3]
        os.system(f"gzip -c test_data/repodata/{base} > /tmp/{src}")
        src_path = f"/tmp/{src}"
    shutil.copy(src_path, download_item.target_path)
    self.logger.info(f"File {src} mock-downloaded.")
    download_item.status_code = 200


def test_phase_1(db_conn, caplog, monkeypatch):
    """Test add product and repo."""

    DatabaseHandler.connection = db_conn
    reset_db(db_conn)
    # delete_all_tables(db_conn)

    # write_testing_data(db_conn)
    basearch = "x86_64"
    releasever = "7Server"
    base_url = "http://localhost:8888/%s/%s" % (releasever, basearch)
    content_set = "content_set_1"
    content_set_label = "Content set 1"

    # Test store product.
    products = {
        "prod1": {
            "product_id": None,
            "content_sets": {content_set: {"name": content_set_label}},
        }
    }
    prod_store = product_store.ProductStore()
    prod_store.store(products)

    monkeypatch.setattr(FileDownloadThread, "_download", download_mock)

    # Test store repo.
    rep_con = RepositoryController()
    rep_con.add_repository(
        repo_url=base_url,
        content_set=content_set,
        basearch=basearch,
        releasever=releasever,
        organization=DEFAULT_ORG_NAME,
    )
    rep_con.import_repositories()

    rep_con1 = RepositoryController()
    rep_con1.add_db_repositories()
    rep_con1.store()

    for file in ["repomd.xml", "updateinfo.xml.gz", "primary_db.sqlite.gz"]:
        assert f"File {file} mock-downloaded." in caplog.messages

    _assert_rows_in_table(db_conn, "content_set", 1)
    _assert_rows_in_table(db_conn, "repo", 1)
    _assert_rows_in_table(db_conn, "package", 18)
    _assert_rows_in_table(db_conn, "errata_refs", 5)
    _assert_rows_in_table(db_conn, "cve", 2)


def test_phase_2(db_conn, monkeypatch):
    """Test delete content set."""

    DatabaseHandler.connection = db_conn
    reset_db(db_conn)

    delete_all_tables(db_conn)
    write_testing_data(db_conn)

    monkeypatch.setattr(FileDownloadThread, "_download", download_mock)

    # Test delete content_set
    rep_con = RepositoryController()

    _assert_rows_in_table(db_conn, "content_set", 2)
    _assert_rows_in_table(db_conn, "package", 7)
    _assert_rows_in_table(db_conn, "repo", 2)

    rep_con.delete_content_set("content set 2")

    _assert_rows_in_table(db_conn, "content_set", 1)
    _assert_rows_in_table(db_conn, "package", 6)
    _assert_rows_in_table(db_conn, "repo", 1)


def _assert_rows_in_table(db_conn, table, n_expected):
    """Check expected rows in given database table."""
    with db_conn.cursor() as cur:
        cur.execute("""select * from %s""" % table)
        rows = cur.fetchall()
        assert len(rows) == n_expected


def delete_all_tables(db_conn):
    """Delete all tables in the database."""
    with db_conn.cursor() as cur:
        cur.execute("TRUNCATE TABLE repo CASCADE")
        cur.execute("TRUNCATE TABLE package CASCADE")
        cur.execute("TRUNCATE TABLE content_set CASCADE")
        cur.execute("TRUNCATE TABLE product CASCADE")
        cur.execute("TRUNCATE TABLE errata CASCADE")
        cur.execute("TRUNCATE TABLE cve CASCADE")
    db_conn.commit()
