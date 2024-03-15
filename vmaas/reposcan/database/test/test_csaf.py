"""Unit tests of csaf_store.py."""
import typing as t
from datetime import datetime
from datetime import timezone

import pytest
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

import vmaas.reposcan.redhatcsaf.modeling as m
from vmaas.reposcan.conftest import reset_db
from vmaas.reposcan.conftest import write_testing_data
from vmaas.reposcan.database.csaf_store import CsafStore


EXISTING_PRODUCTS = [
    m.CsafProduct("cpe1000", "pkg1000", 4, None),
    m.CsafProduct("cpe1001", "pkg1001-1:1-1.noarch", 3, None),
    m.CsafProduct("cpe1002", "pkg1002", 4, "module:1"),
    m.CsafProduct("cpe1003", "pkg1003-1:1-1.noarch", 3, "module:1"),
]
NEW_PRODUCTS = [
    m.CsafProduct("cpe1000", "pkg1001", 4, None),
    m.CsafProduct("cpe1001", "pkg1000-1:1-1.noarch", 3, None),
    m.CsafProduct("cpe1002", "pkg1003", 4, "module:1"),
    m.CsafProduct("cpe1003", "pkg1002-1:1-1.noarch", 3, "module:1"),
    m.CsafProduct("cpe1002", "pkg1003", 4, "module:2"),
    m.CsafProduct("cpe1003", "pkg1002-1:1-1.noarch", 3, "module:2"),
]


# pylint: disable=protected-access
class TestCsafStore:
    """CsafStore tests."""

    @pytest.fixture
    def csaf_store(self, db_conn: connection) -> t.Generator[CsafStore, None, None]:  # pylint: disable=unused-argument
        """Fixture returning CsafStore obj and cleaning db after test."""
        store = CsafStore()
        yield store
        reset_db(store.conn)

    @pytest.fixture
    def products(self, csaf_store: CsafStore) -> t.Generator[None, None, None]:
        """Setup products in DB."""
        timestamp = datetime.now()
        write_testing_data(csaf_store.conn)
        cpes = ((1000, "cpe1000"), (1001, "cpe1001"), (1002, "cpe1002"), (1003, "cpe1003"))
        package_names = ((1000, "pkg1000"), (1001, "pkg1001"), (1002, "pkg1002"), (1003, "pkg1003"))
        packages = (
            (1000, 1000, 201, 1, timestamp),
            (1001, 1001, 201, 1, timestamp),
            (1002, 1002, 201, 1, timestamp),
            (1003, 1003, 201, 1, timestamp),
        )
        products = (
            (1000, 1000, 1000, None, None),
            (1001, 1001, None, 1001, None),
            (1002, 1002, 1002, None, "module:1"),
            (1003, 1003, None, 1003, "module:1"),
        )
        cur = csaf_store.conn.cursor()
        execute_values(cur, "INSERT INTO csaf_file(id, name, updated) VALUES %s RETURNING id", ((1, "file1", timestamp),))
        execute_values(cur, "INSERT INTO cpe(id, label) VALUES %s RETURNING id", cpes)
        execute_values(cur, "INSERT INTO package_name(id, name) VALUES %s RETURNING id", package_names)
        execute_values(
            cur, "INSERT INTO package(id, name_id, evr_id, arch_id, modified) VALUES %s RETURNING id", packages
        )
        execute_values(
            cur,
            "INSERT INTO csaf_product(id, cpe_id, package_name_id, package_id, module_stream) VALUES %s RETURNING id",
            products,
        )
        csaf_store.conn.commit()
        cur.close()

        yield

        reset_db(csaf_store.conn)

    def test_save_file(self, csaf_store: CsafStore) -> None:
        """Test saving csaf file."""
        now = datetime.now(timezone.utc)
        csaf_store._save_csaf_files(m.CsafFiles({"file": m.CsafFile("file", now, cves=["CVE-2024-1234"])}))
        cur = csaf_store.conn.cursor()
        cur.execute("SELECT id, name FROM csaf_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        id_save = res[0]
        assert "CVE-2024-1234" in csaf_store.cve2file_id
        assert csaf_store.cve2file_id["CVE-2024-1234"] == id_save

        # update row
        update_ts = datetime.now(timezone.utc)
        csaf_store._save_csaf_files(m.CsafFiles({"file": m.CsafFile("file", update_ts, cves=["CVE-2024-1234"])}))
        cur.execute("SELECT id, updated FROM csaf_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        assert res[0] == id_save
        assert res[1] == update_ts

    def test_get_product_attr_id(self, csaf_store: CsafStore) -> None:
        """Test getting product attribute_id."""
        mapping = {"key": 9}
        res = csaf_store._get_product_attr_id("some_attr", mapping, "key")
        assert res == 9

        with pytest.raises(KeyError):
            csaf_store._get_product_attr_id("some_attr", mapping, "bad_key")

    def test_load_product_attr_ids(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test loading product atrribute_id."""
        csaf_store = CsafStore()
        products_obj = m.CsafProducts(
            EXISTING_PRODUCTS
            + [
                # will be skipped - missing cpe
                m.CsafProduct("cpe_missing", "pkg1000", 4, None),
                # will be skipped - missing package
                m.CsafProduct("cpe1000", "pkg_missing", 4, None),
            ]
        )
        csaf_store._load_product_attr_ids(products_obj)
        assert len(products_obj) == 4
        for product in products_obj:
            assert product.cpe_id
            assert product.package_name_id or product.package_id

    def test_update_product_ids(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test loading product ids."""
        csaf_store = CsafStore()
        products_obj = m.CsafProducts(EXISTING_PRODUCTS + NEW_PRODUCTS)
        csaf_store._update_product_ids(products_obj)
        for i, product in enumerate(products_obj):
            if i < len(EXISTING_PRODUCTS):
                assert product.id_
            else:
                assert not product.id_

    def test_insert_missing_products(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test inserting missing product ids."""
        csaf_store = CsafStore()
        products_obj = m.CsafProducts(EXISTING_PRODUCTS + NEW_PRODUCTS)
        csaf_store._update_product_ids(products_obj)
        csaf_store._insert_missing_products(products_obj)
        ids = []
        for product in products_obj:
            assert product.id_
            assert product.id_ not in ids
            ids.append(product.id_)

    def assert_cve_count(self, csaf_store: CsafStore, count: int) -> None:
        """Assert cve count in db"""
        cur = csaf_store.conn.cursor()
        cur.execute("SELECT id FROM cve WHERE UPPER(name) = %s", ("CVE-0000-0001",))
        cve_id = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM csaf_cve_product WHERE cve_id = %s", (cve_id,))
        db_count = cur.fetchone()[0]
        assert db_count == count

    def test_insert_cves(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test inserting csaf_cve_product."""
        csaf_store = CsafStore()
        csaf_store.cve2file_id["CVE-0000-0001"] = 1
        products_obj = m.CsafProducts(EXISTING_PRODUCTS)
        csaf_store._update_product_ids(products_obj)
        csaf_store._insert_cves("CVE-0000-0001", products_obj)
        self.assert_cve_count(csaf_store, 4)

    def test_insert_cves_no_product_ids(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test inserting csaf_cve_product."""
        csaf_store = CsafStore()
        csaf_store.cve2file_id["CVE-0000-0001"] = 1
        products_obj = m.CsafProducts([m.CsafProduct("cpe1000", "pkg1000", 4, None)])
        csaf_store._insert_cves("CVE-0000-0001", products_obj)
        self.assert_cve_count(csaf_store, 0)

    def test_remove_cves(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test removing csaf_cve_product."""
        csaf_store = CsafStore()
        csaf_store.cve2file_id["CVE-0000-0001"] = 1
        products_obj = m.CsafProducts([m.CsafProduct("cpe1000", "pkg1000", 4, None)])
        csaf_store._update_product_ids(products_obj)
        csaf_store._insert_cves("CVE-0000-0001", products_obj)
        self.assert_cve_count(csaf_store, 1)

        # remove old cve-product
        products_obj = m.CsafProducts([m.CsafProduct("cpe1001", "pkg1001-1:1-1.noarch", 3, None)])
        csaf_store._update_product_ids(products_obj)
        csaf_store._remove_cves("CVE-0000-0001", products_obj)
        self.assert_cve_count(csaf_store, 0)
