"""Cache test."""
# pylint: disable=redefined-outer-name

import os
import sqlite3

import pytest

from vmaas.webapp.cache import Cache

TEST_DUMP_FILE = "/tmp/cache_test.db"
TEST_SQL_SCRIPT = "test/data/cache-dump.sql"


@pytest.fixture(scope="session")
def dump_file_db():
    """Create testing sqlite file."""
    if os.path.exists(TEST_DUMP_FILE):
        os.remove(TEST_DUMP_FILE)
    with sqlite3.connect(TEST_DUMP_FILE) as conn:
        with open(TEST_SQL_SCRIPT, "r", encoding='utf8') as sql_script:
            conn.cursor().executescript(sql_script.read())


# pylint: disable=unused-argument
@pytest.fixture()
def cache(dump_file_db, monkeypatch):
    """Fixture of cache instance."""
    monkeypatch.setattr(Cache, 'download', lambda _: True)
    cache = Cache(TEST_DUMP_FILE)
    cache.reload()
    return cache


def test_load(cache):
    """Test cache load method"""
    assert len(cache.arch2id) == 32
    assert len(cache.arch_compat) == 28
    assert len(cache.cve_detail) == 1
    assert len(cache.dbchange) == 5
    assert len(cache.errata_detail) == 3
    assert len(cache.errataid2name) == 3
    assert len(cache.errataid2repoids) == 3
    assert len(cache.evr2id) == 6
    assert len(cache.id2arch) == 32
    assert len(cache.id2evr) == 6
    assert len(cache.id2packagename) == 4
    assert len(cache.modulename2id) == 2
    assert len(cache.nevra2pkgid) == 7
    assert len(cache.package_details) == 7
    assert len(cache.packagename2id) == 4
    assert len(cache.pkgerrata2module) == 3
    assert len(cache.pkgid2errataids) == 6
    assert len(cache.pkgid2repoids) == 7
    assert len(cache.repo_detail) == 2
    assert len(cache.repolabel2ids) == 2
    assert len(cache.repopath2ids) == 2
    assert len(cache.src_pkg_id2pkg_ids) == 2
    assert len(cache.updates) == 4
    assert len(cache.updates_index) == 4
    assert len(cache.content_set_id2label) == 2
    assert len(cache.label2content_set_id) == 2
    assert len(cache.content_set_id2pkg_name_ids) == 2


def test_clear(cache):
    """Test cache clear method"""
    cache.clear()
    variables = vars(cache)
    assert len(variables) == 36
    for name, var in variables.items():
        if name == "filename":
            assert var == TEST_DUMP_FILE
        elif name == "package_details_modified_index":
            assert var == []
        else:
            assert var == {}


def test_repopath2ids(cache):
    """Test repopath2ids cache"""
    assert len(cache.repopath2ids) == 2

    assert cache.repopath2ids["/repo1"] is not None
    assert len(cache.repopath2ids["/repo1"]) == 1
    assert cache.repopath2ids["/repo1"][0] == 801

    assert cache.repopath2ids["/repo2"] is not None
    assert len(cache.repopath2ids["/repo2"]) == 1
    assert cache.repopath2ids["/repo2"][0] == 802
