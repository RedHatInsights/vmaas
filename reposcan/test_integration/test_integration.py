"""
Unit test classes for repository controller module.
"""

import os
import shutil
import pytest

from repodata.repository_controller import RepositoryController

from database import product_store
from download.downloader import DownloadItem, FileDownloadThread


def download_mock(self, download_item: DownloadItem):
    """Mock downloading function with copying from
    testing data directory."""
    src = download_item.source_url.split('/')[-1]
    src_path = 'test_data/repodata/integration/' + src
    if src.endswith('.gz'):  # prepare archive file
        base = src[:-3]
        os.system(f"gzip -c test_data/repodata/{base} > /tmp/{src}")
        src_path = f"/tmp/{src}"
    shutil.copy(src_path, download_item.target_path)
    self.logger.info(f"File {src} mock-downloaded.")
    download_item.status_code = 200


@pytest.mark.first
def test_phase_1(db_conn, caplog, monkeypatch):
    """Test add product and repo."""
    basearch = 'x86_64'
    releasever = '7Server'
    base_url = 'http://localhost:8888/%s/%s' % (releasever, basearch)
    content_set = 'content_set_1'
    content_set_label = 'Content set 1'

    # Test store product.
    products = dict(prod1=dict(product_id=None, content_sets={content_set: {"name": content_set_label}}))
    prod_store = product_store.ProductStore()
    prod_store.store(products)

    monkeypatch.setattr(FileDownloadThread, '_download', download_mock)

    # Test store repo.
    rep_con = RepositoryController()
    rep_con.add_repository(repo_url=base_url, content_set=content_set,
                           basearch=basearch, releasever=releasever)
    rep_con.import_repositories()

    rep_con1 = RepositoryController()
    rep_con1.add_db_repositories()
    rep_con1.store()

    for file in ["repomd.xml", "updateinfo.xml.gz", "primary_db.sqlite.gz"]:
        assert f"File {file} mock-downloaded." in caplog.messages

    with db_conn.cursor() as cur:
        cur.execute("""select * from content_set""")
        rows = cur.fetchall()
        assert len(rows) == 1

        cur.execute("""select * from repo""")
        rows = cur.fetchall()
        assert len(rows) == 1

        cur.execute("""select * from package""")
        rows = cur.fetchall()
        assert len(rows) == 18

        cur.execute("""select * from errata_refs""")
        rows = cur.fetchall()
        assert len(rows) == 5

        cur.execute("""select * from cve""")
        rows = cur.fetchall()
        assert len(rows) == 2


def test_phase_2(db_conn, monkeypatch):
    """Test add cves and delete content set."""
    monkeypatch.setattr(FileDownloadThread, '_download', download_mock)

    # Test delete content_set
    rep_con = RepositoryController()
    rep_con.delete_content_set("content_set_1")

    with db_conn.cursor() as cur:
        cur.execute("""select * from package""")
        rows = cur.fetchall()
        assert len(rows) == 6

        cur.execute("""select * from errata_refs""")
        rows = cur.fetchall()
        assert not rows
