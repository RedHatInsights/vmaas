"""Unit tests of vexfeed_store.py."""
import typing as t
from datetime import datetime
from datetime import timezone

import pytest
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

import vmaas.reposcan.redhatcsaf.modeling as m
from vmaas.reposcan.conftest import reset_db
from vmaas.reposcan.conftest import write_testing_data
from vmaas.reposcan.database.vexfeed_store import VexFeedStore


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
class TestVexFeedStore:
    """VexFeedStore tests."""

    @pytest.fixture
    def vexfeed_store(self, db_conn: connection) -> t.Generator[VexFeedStore, None, None]:  # pylint: disable=unused-argument
        """Fixture returning VexFeedStore obj and cleaning db after test."""
        store = VexFeedStore()
        yield store
        reset_db(store.conn)

    @pytest.fixture
    def products(self, vexfeed_store: VexFeedStore) -> t.Generator[None, None, None]:
        """Setup products in DB using vexfeed_* tables."""
        timestamp = datetime.now()
        write_testing_data(vexfeed_store.conn)
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
        cur = vexfeed_store.conn.cursor()
        execute_values(cur, "INSERT INTO vexfeed_file(id, name, updated) VALUES %s RETURNING id", ((1, "file1", None),))
        execute_values(cur, "INSERT INTO cpe(id, label) VALUES %s RETURNING id", cpes)
        execute_values(cur, "INSERT INTO package_name(id, name) VALUES %s RETURNING id", package_names)
        execute_values(
            cur, "INSERT INTO package(id, name_id, evr_id, arch_id, modified) VALUES %s RETURNING id", packages
        )
        execute_values(
            cur,
            "INSERT INTO vexfeed_product(id, cpe_id, package_name_id, package_id, module_stream) VALUES %s RETURNING id",
            products,
        )
        vexfeed_store.conn.commit()
        cur.close()

        yield

        reset_db(vexfeed_store.conn)

    @pytest.fixture
    def files_obj_for_insert(self) -> tuple[m.CsafFiles, datetime]:
        """Vexfeed files obj for insert_cves tests."""
        now = datetime.now(timezone.utc)
        files_obj = m.CsafFiles({"file": m.CsafFile("file", now, None, id_=1, cves=[CVE], cve_file_timestamp=now)})
        return files_obj, now

    @pytest.fixture
    def store_cve_product(self) -> VexFeedStore:  # pylint: disable=unused-argument
        """VexFeedStore object with 1 inserted CVE-product in DB"""
        store = VexFeedStore()
        store.cve2file_id[CVE] = 1
        products_obj = m.CsafProducts([m.CsafProduct("cpe1000", "pkg1000", 4, None)])
        store._update_product_ids(products_obj)
        store._insert_cves(CVE, products_obj)
        self.assert_cve_count(store, 1)
        return store

    def test_delete_vexfeed_files(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test removing vexfeed files."""
        store = VexFeedStore()
        now = datetime.now(timezone.utc)
        files = m.CsafFiles(
            {"file1": m.CsafFile("file1", now, id_=1), "file2": m.CsafFile("file2", now, in_source=True)}
        )
        store.delete_csaf_files(files.not_in_source_files)
        cur = store.conn.cursor()
        cur.execute("SELECT id FROM vexfeed_file WHERE name = 'file1'")
        res = cur.fetchone()
        assert not res

        cur.execute("SELECT id FROM vexfeed_cve_product WHERE vexfeed_file_id = 1")
        res = cur.fetchone()
        assert not res

    def test_save_file(self, vexfeed_store: VexFeedStore) -> None:
        """Test saving vexfeed file."""
        cve = "CVE-2024-1234"
        now = datetime.now(timezone.utc)
        files = m.CsafFiles(
            {"file": m.CsafFile("file", now, cves=[cve], cve_file_timestamp=now), "file2": m.CsafFile("file2", now, cves=[CVE], cve_file_timestamp=now)}
        )
        vexfeed_store._save_csaf_files(files)
        cur = vexfeed_store.conn.cursor()
        cur.execute("SELECT id, name FROM vexfeed_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        id_save = res[0]
        assert cve in vexfeed_store.cve2file_id
        assert vexfeed_store.cve2file_id[cve] == id_save
        for file in files:
            assert file.id_

        # update row
        vexfeed_store.cve2file_id = {}
        update_ts = datetime.now(timezone.utc)
        files = m.CsafFiles({"file": m.CsafFile("file", update_ts, cves=[cve], cve_file_timestamp=update_ts)})
        vexfeed_store._save_csaf_files(files)
        cur.execute("SELECT id, updated FROM vexfeed_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        assert res[0] == id_save
        assert res[1] is None
        assert cve in vexfeed_store.cve2file_id
        assert vexfeed_store.cve2file_id[cve] == id_save
        # update timestamp
        vexfeed_store._update_file_timestamp(cve, files)
        cur.execute("SELECT id, updated FROM vexfeed_file WHERE name = 'file'")
        res = cur.fetchone()
        assert res
        assert res[0] == id_save
        assert res[1] == update_ts

    def test_save_empty_files(self, vexfeed_store: VexFeedStore) -> None:
        """Test saving empty vexfeed files."""
        files = m.CsafFiles()
        vexfeed_store._save_csaf_files(files)
        cur = vexfeed_store.conn.cursor()
        cur.execute("SELECT id, name FROM vexfeed_file WHERE name = 'file'")
        res = cur.fetchone()
        assert not res

    def test_get_product_attr_id(self, vexfeed_store: VexFeedStore) -> None:
        """Test getting product attribute_id."""
        mapping = {"key": 9}
        res = vexfeed_store._get_product_attr_id("some_attr", mapping, "key")
        assert res == 9

        with pytest.raises(KeyError):
            vexfeed_store._get_product_attr_id("some_attr", mapping, "bad_key")

    def test_load_product_attr_ids(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test loading product attribute_id."""
        store = VexFeedStore()
        products_obj = m.CsafProducts(
            EXISTING_PRODUCTS
            + [
                m.CsafProduct("cpe_missing", "pkg1000", 4, None),
                m.CsafProduct("cpe1000", "pkg_missing", 4, None),
            ]
        )
        store._load_product_attr_ids(products_obj)
        assert len(products_obj) == len(EXISTING_PRODUCTS) + 2
        for product in products_obj:
            assert product.cpe_id
            assert product.package_name_id or product.package_id

    def test_update_product_ids(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test loading product ids from vexfeed_product table."""
        store = VexFeedStore()
        products_obj = m.CsafProducts(EXISTING_PRODUCTS + NEW_PRODUCTS)
        store._update_product_ids(products_obj)
        for i, product in enumerate(products_obj):
            if i < len(EXISTING_PRODUCTS):
                assert product.id_
            else:
                assert not product.id_

    def test_insert_missing_products(self, products: None) -> None:  # pylint: disable=unused-argument
        """Test inserting missing product ids into vexfeed_product."""
        store = VexFeedStore()
        products_obj = m.CsafProducts(EXISTING_PRODUCTS + NEW_PRODUCTS)
        store._update_product_ids(products_obj)
        store._insert_missing_products(products_obj)
        ids = []
        for product in products_obj:
            assert product.id_
            assert product.id_ not in ids
            ids.append(product.id_)

    def assert_cve_count(self, store: VexFeedStore, count: int) -> None:
        """Assert cve count in db."""
        cur = store.conn.cursor()
        cur.execute("SELECT id FROM cve WHERE UPPER(name) = %s", (CVE,))
        cve_id = cur.fetchone()[0]
        cur.execute("SELECT count(*) FROM vexfeed_cve_product WHERE cve_id = %s", (cve_id,))
        db_count = cur.fetchone()[0]
        assert db_count == count

    def assert_file_timestamp(self, store: VexFeedStore, timestamp: datetime | None, id_: int = 1) -> None:
        """Assert vexfeed_file timestamp after insert."""
        cur = store.conn.cursor()
        cur.execute("SELECT updated FROM vexfeed_file WHERE id = %s", (id_,))
        updated = cur.fetchone()[0]
        assert updated == timestamp

    def test_insert_cves(  # pylint: disable=unused-argument
        self, products: None, files_obj_for_insert: tuple[m.CsafFiles, datetime]
    ) -> None:
        """Test inserting vexfeed_cve_product."""
        store = VexFeedStore()
        store.cve2file_id[CVE] = 1
        files, timestamp = files_obj_for_insert
        products_obj = m.CsafProducts(EXISTING_PRODUCTS)
        store._update_product_ids(products_obj)
        store._insert_cves(CVE, products_obj)
        store._update_file_timestamp(CVE, files)
        self.assert_cve_count(store, 4)
        self.assert_file_timestamp(store, timestamp)

    def test_insert_cves_no_product_ids(  # pylint: disable=unused-argument
        self, products: None, files_obj_for_insert: tuple[m.CsafFiles, datetime]
    ) -> None:
        """Test inserting vexfeed_cve_product without product ids."""
        store = VexFeedStore()
        store.cve2file_id[CVE] = 1
        files, timestamp = files_obj_for_insert
        products_obj = m.CsafProducts([m.CsafProduct("cpe1000", "pkg1000", 4, None)])
        store._insert_cves(CVE, products_obj)
        store._update_file_timestamp(CVE, files)
        self.assert_cve_count(store, 0)
        self.assert_file_timestamp(store, timestamp)

    def test_insert_cves_unknown_cpe(  # pylint: disable=unused-argument
        self, products: None, files_obj_for_insert: tuple[m.CsafFiles, datetime]
    ) -> None:
        """Test inserting vexfeed_cve_product with unknown CPE."""
        store = VexFeedStore()
        store.cve2file_id[CVE] = 1
        files, timestamp = files_obj_for_insert
        products_obj = m.CsafProducts([m.CsafProduct("cpe_unknown", "pkg1000", 4, None)])
        store._update_product_ids(products_obj)
        store._insert_missing_products(products_obj)
        store._insert_cves(CVE, products_obj)
        store._update_file_timestamp(CVE, files)
        self.assert_cve_count(store, 1)
        self.assert_file_timestamp(store, timestamp)

    @pytest.mark.parametrize(
        "products_obj",
        [m.CsafProducts([m.CsafProduct("cpe1001", "pkg1001-1:1-1.noarch", 3, None)]), m.CsafProducts()],
        ids=("fixed_product", "no_products"),
    )
    def test_remove_cves(  # pylint: disable=unused-argument
        self,
        products: None,
        files_obj_for_insert: tuple[m.CsafFiles, datetime],
        store_cve_product: VexFeedStore,
        products_obj: m.CsafProducts,
    ) -> None:
        """Test removing vexfeed_cve_product."""
        store = store_cve_product
        files, timestamp = files_obj_for_insert

        store._update_product_ids(products_obj)
        store._remove_cves(CVE, products_obj)
        store._update_file_timestamp(CVE, files)
        self.assert_cve_count(store, 0)
        self.assert_file_timestamp(store, timestamp)

    def test_store_end_to_end(self, vexfeed_store: VexFeedStore) -> None:
        """Test the full store() pipeline: files → products → cves → vexfeed tables."""
        cve = "CVE-2026-9999"
        timestamp = datetime.now(timezone.utc)
        affected_package = "affected-package"
        fixed_package = "fixed-package-1:2.3.4-5.el9.x86_64"
        csaf_data = m.CsafData(
            files=m.CsafFiles(
                {"file": m.CsafFile("file", timestamp, cves=[cve], cve_file_timestamp=timestamp)}
            ),
            cves=m.CsafCves(
                {
                    cve: m.CsafProducts(
                        [
                            m.CsafProduct("cpe:/o:redhat:enterprise_linux:9", affected_package, 4),
                            m.CsafProduct("cpe:/o:redhat:enterprise_linux:9", fixed_package, 3),
                        ]
                    )
                }
            ),
        )
        cur = vexfeed_store.conn.cursor()
        cur.execute("INSERT INTO cve (name) VALUES (%s)", (cve,))
        vexfeed_store.conn.commit()

        vexfeed_store.store(csaf_data)

        cur.execute("SELECT name FROM package_name ORDER BY name")
        assert cur.fetchall() == [(affected_package,), ("fixed-package",)]
        cur.execute(
            """
            SELECT package_name.name, vexfeed_product.package_id IS NOT NULL
            FROM vexfeed_cve_product
            JOIN vexfeed_product ON vexfeed_cve_product.vexfeed_product_id = vexfeed_product.id
            JOIN package_name ON vexfeed_product.package_name_id = package_name.id
            WHERE vexfeed_cve_product.cve_id = (SELECT id FROM cve WHERE name = %s)
            ORDER BY package_name.name
            """,
            (cve,),
        )
        assert cur.fetchall() == [(affected_package, False), ("fixed-package", True)]
        cur.close()

    def test_delete_unreferenced(self, vexfeed_store: VexFeedStore) -> None:
        """Test that orphaned vexfeed_products are cleaned up."""
        cur = vexfeed_store.conn.cursor()
        cur.execute("INSERT INTO cpe(id, label) VALUES (9999, 'cpe_orphan')")
        cur.execute("INSERT INTO package_name(id, name) VALUES (9999, 'pkg_orphan')")
        cur.execute(
            "INSERT INTO vexfeed_product(cpe_id, package_name_id) VALUES (9999, 9999) RETURNING id"
        )
        orphan_id = cur.fetchone()[0]
        vexfeed_store.conn.commit()

        vexfeed_store.delete_unreferenced_products()

        cur.execute("SELECT id FROM vexfeed_product WHERE id = %s", (orphan_id,))
        assert cur.fetchone() is None
        cur.close()
