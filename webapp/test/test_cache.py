"""Cache test."""

from test import yaml_cache

from cache import Cache


TEST_DUMP_FILE = "/tmp/cache_test.shelve"


def test_cache(monkeypatch):
    """Test cache load and clear method"""

    monkeypatch.setattr(Cache, 'download', lambda _: True)

    cache_test = yaml_cache.load_test_cache()
    cache_test.dump_shelve(TEST_DUMP_FILE)

    cache = Cache(TEST_DUMP_FILE)
    assert len(cache.arch2id) == 3
    assert len(cache.arch_compat) == 2
    assert len(cache.cve_detail) == 1
    assert len(cache.dbchange) == 5
    assert len(cache.errata_detail) == 4
    assert len(cache.errataid2name) == 4
    assert len(cache.errataid2repoids) == 1
    assert len(cache.evr2id) == 7
    assert len(cache.id2arch) == 3
    assert len(cache.id2evr) == 7
    assert len(cache.id2packagename) == 3
    assert len(cache.modulename2id) == 2
    assert len(cache.nevra2pkgid) == 5
    assert len(cache.package_details) == 8
    assert len(cache.packagename2id) == 3
    assert len(cache.pkgerrata2module) == 5
    assert len(cache.pkgid2errataids) == 7
    assert len(cache.pkgid2repoids) == 5
    assert len(cache.productid2repoids) == 1
    assert len(cache.repo_detail) == 5
    assert len(cache.repolabel2ids) == 1
    assert len(cache.src_pkg_id2pkg_ids) == 2
    assert len(cache.updates) == 1
    assert len(cache.updates_index) == 1

    cache.clear()
    variables = vars(cache)
    assert len(variables) == 26
    for name, var in variables.items():
        if name == "filename":
            assert var == TEST_DUMP_FILE
        else:
            assert var == {}
