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
CVE = "CVE-0000-0001"


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
            (1001, 1001, 1001, 1001, None),
            (1002, 1002, 1002, None, "module:1"),
            (1003, 1003, 1003, 1003, "module:1"),
        )
        cur = csaf_store.conn.cursor()
        execute_values(cur, "INSERT INTO csaf_file(id, name, updated) VALUES %s RETURNING id", ((1, "file1", None),))
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

    @pytest.fixture
    def files_obj_for_insert(self) -> tuple[m.CsafFiles, datetime]:
        """Csaf files obj for insert_cves tests."""
        now = datetime.now(timezone.utc)
        files_obj = m.CsafFiles({"file": m.CsafFile("file", now, None, id_=1, cves=[CVE])})
        return files_obj, now

    @pytest.fixture
    def store_cve_product(self) -> CsafStore:  # pylint: disable=unused-argument
        """CsafStore object with 1 inserted CVE-product in DB"""
        csaf_store = CsafStore()
        csaf_store.cve2file_id[CVE] = 1
        products_obj = m.CsafProducts([m.CsafProduct("cpe1000", "pkg1000", 4, None)])
        csaf_store._update_product_ids(products_obj)
        csaf_store._insert_cves(CVE, products_obj)
        self.assert_cve_count(csaf_store, 1)
        return csaf_store

    def test_delete_csaf_files(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test removing csaf files"""
        csaf_store = CsafStore()
        now = datetime.now(timezone.utc)
        files = m.CsafFiles(
            {"file1": m.CsafFile("file1", now, id_=1), "file2": m.CsafFile("file2", now, csv=True)}
        )
        csaf_store._delete_csaf_files(files)
        cur = csaf_store.conn.cursor()
        cur.execute("SELECT id FROM csaf_file WHERE name = 'file1'")
        res = cur.fetchone()
        assert not res

        cur.execute("SELECT id FROM csaf_cve_product WHERE csaf_file_id = 1")
        res = cur.fetchone()
        assert not res

    def test_save_file(self, csaf_store: CsafStore) -> None:
        """Test saving csaf file."""
        cve = "CVE-2024-1234"
        now = datetime.now(timezone.utc)
        files = m.CsafFiles(
            {"file": m.CsafFile("file", now, cves=[cve]), "file2": m.CsafFile("file2", now, cves=[CVE])}
        )
        csaf_store._save_csaf_files(files)
        cur = csaf_store.conn.cursor()
        cur.execute("SELECT id, name FROM csaf_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        id_save = res[0]
        assert cve in csaf_store.cve2file_id
        assert csaf_store.cve2file_id[cve] == id_save
        for file in files:
            assert file.id_

        # update row
        csaf_store.cve2file_id = {}  # reset cve2file mapping
        update_ts = datetime.now(timezone.utc)
        files = m.CsafFiles({"file": m.CsafFile("file", update_ts, cves=[cve])})
        # save should not update timestamp
        csaf_store._save_csaf_files(files)
        cur.execute("SELECT id, updated FROM csaf_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        assert res[0] == id_save
        assert res[1] is None
        assert cve in csaf_store.cve2file_id
        assert csaf_store.cve2file_id[cve] == id_save
        # update timestamp
        csaf_store._update_file_timestamp(cve, files)
        cur.execute("SELECT id, updated FROM csaf_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        assert res[0] == id_save
        assert res[1] == update_ts

    def test_save_empty_csaf_files(self, csaf_store: CsafStore) -> None:
        """Test saving empty csaf files."""
        files = m.CsafFiles()
        csaf_store._save_csaf_files(files)
        cur = csaf_store.conn.cursor()
        cur.execute("SELECT id, name FROM csaf_file WHERE name = 'file'")
        res = cur.fetchone()
        assert not res

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
                # will be inserted - missing package
                m.CsafProduct("cpe1000", "pkg_missing", 4, None),
            ]
        )
        csaf_store._load_product_attr_ids(products_obj)
        assert len(products_obj) == len(EXISTING_PRODUCTS) + 1  # existing + missing cpe
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
        cur.execute("SELECT id FROM cve WHERE UPPER(name) = %s", (CVE,))
        cve_id = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM csaf_cve_product WHERE cve_id = %s", (cve_id,))
        db_count = cur.fetchone()[0]
        assert db_count == count

    def assert_file_timestamp(self, csaf_store: CsafStore, timestamp: datetime | None, id_: int = 1) -> None:
        """Assert csaf_file timestamp after insert"""
        cur = csaf_store.conn.cursor()
        cur.execute("SELECT updated FROM csaf_file WHERE id = %s", (id_,))
        updated = cur.fetchone()[0]
        assert updated == timestamp

    def test_insert_cves(  # pylint: disable=unused-argument
        self, products: None, files_obj_for_insert: tuple[m.CsafFiles, datetime]
    ) -> None:
        """Test inserting csaf_cve_product."""
        csaf_store = CsafStore()
        csaf_store.cve2file_id[CVE] = 1
        files, timestamp = files_obj_for_insert
        products_obj = m.CsafProducts(EXISTING_PRODUCTS)
        csaf_store._update_product_ids(products_obj)
        csaf_store._insert_cves(CVE, products_obj)
        csaf_store._update_file_timestamp(CVE, files)
        self.assert_cve_count(csaf_store, 4)
        self.assert_file_timestamp(csaf_store, timestamp)

    def test_insert_cves_no_product_ids(  # pylint: disable=unused-argument
        self, products: None, files_obj_for_insert: tuple[m.CsafFiles, datetime]
    ) -> None:
        """Test inserting csaf_cve_product."""
        csaf_store = CsafStore()
        csaf_store.cve2file_id[CVE] = 1
        files, timestamp = files_obj_for_insert
        products_obj = m.CsafProducts([m.CsafProduct("cpe1000", "pkg1000", 4, None)])
        csaf_store._insert_cves(CVE, products_obj)
        csaf_store._update_file_timestamp(CVE, files)
        self.assert_cve_count(csaf_store, 0)
        # file timestamp is updated also if CVE is skipped when no products are matched
        self.assert_file_timestamp(csaf_store, timestamp)

    def test_insert_cves_unknown_cpe(  # pylint: disable=unused-argument
        self, products: None, files_obj_for_insert: tuple[m.CsafFiles, datetime]
    ) -> None:
        """Test inserting csaf_cve_product."""
        csaf_store = CsafStore()
        csaf_store.cve2file_id[CVE] = 1
        files, timestamp = files_obj_for_insert
        products_obj = m.CsafProducts([m.CsafProduct("cpe_unknown", "pkg1000", 4, None)])
        csaf_store._update_product_ids(products_obj)
        # insert product with missing cpe
        csaf_store._insert_missing_products(products_obj)
        csaf_store._insert_cves(CVE, products_obj)
        csaf_store._update_file_timestamp(CVE, files)
        self.assert_cve_count(csaf_store, 1)
        self.assert_file_timestamp(csaf_store, timestamp)

    @pytest.mark.parametrize(
        "products_obj",
        [m.CsafProducts([m.CsafProduct("cpe1001", "pkg1001-1:1-1.noarch", 3, None)]), m.CsafProducts()],
        ids=("fixed_product", "no_products"),
    )
    def test_remove_cves(  # pylint: disable=unused-argument
        self,
        products: None,
        files_obj_for_insert: tuple[m.CsafFiles, datetime],
        store_cve_product: CsafStore,
        products_obj: m.CsafProducts,
    ) -> None:
        """Test removing csaf_cve_product."""
        csaf_store = store_cve_product
        files, timestamp = files_obj_for_insert

        # remove old cve-product
        csaf_store._update_product_ids(products_obj)
        csaf_store._remove_cves(CVE, products_obj)
        csaf_store._update_file_timestamp(CVE, files)
        self.assert_cve_count(csaf_store, 0)
        self.assert_file_timestamp(csaf_store, timestamp)
