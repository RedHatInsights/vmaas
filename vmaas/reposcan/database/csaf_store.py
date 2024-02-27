"""
Module containing classes for fetching/importing CSAF data from/into database.
"""
from collections import defaultdict
from psycopg2.extras import execute_values

from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.reposcan.mnm import CSAF_FAILED_DELETE, CSAF_FAILED_IMPORT, CSAF_FAILED_UPDATE
from vmaas.reposcan.redhatcsaf.modeling import CsafCves, CsafData
from vmaas.reposcan.redhatcsaf.modeling import CsafFiles


class CsafStore(ObjectStore):
    """Class providing interface for fetching/importing CSAF data from/into the DB."""

    def __init__(self):
        super().__init__()
        self.csaf_file_map = self._prepare_table_map(cols=("name",), to_cols=("id", "updated"), table="csaf_file")

    def delete_csaf_file(self, name: str):
        """Deletes csaf file from DB."""
        db_id = self.csaf_file_map[name][0]
        cur = self.conn.cursor()
        try:
            cur.execute("delete from oval_file where id = %s", (db_id,))
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("Failed to delete csaf file.")
            self.conn.rollback()
        finally:
            cur.close()

    def _save_csaf_files(self, csaf_files: CsafFiles) -> list[int]:
        cur = self.conn.cursor()
        db_ids = execute_values(
            cur,
            """
                insert into csaf_file (name, updated) values %s
                on conflict (name) do update set updated = excluded.updated
                returning id
            """,
            csaf_files.to_tuples(("name", "csv_timestamp")),
            fetch=True,
        )
        cur.close()
        self.conn.commit()
        return db_ids

    def _get_product_rows(self, products_by_status) -> tuple[dict[str, list[tuple[str, str, str]]], list[tuple[int, str]]]:
        to_associate_ids = []
        to_insert = defaultdict(list)
        try:
            cur = self.conn.cursor()
            for status, products in products_by_status.items():
                if not products:
                    continue
                cur.execute("""SELECT id, cpe, package, module
                                FROM csaf_products
                                WHERE ((cpe, package, module) in %s AND module IS NOT NULL)
                                    OR ((cpe, package) in %s AND module IS NULL)""",
                            (tuple(products), tuple((cpe, package) for cpe, package, _ in products)))
                rows = cur.fetchall()
                for row in rows:
                    to_associate_ids.append((row[0], status))
                for product in products:
                    insert = True
                    for row in rows:
                        if product == (row[1], row[2], row[3]):
                            insert = False
                            break
                    if insert:
                        to_insert[status].append(product)

        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            self.logger.exception("Failure while fetching CSAF products from the DB: %s", exc)
        finally:
            cur.close()

        return to_insert, to_associate_ids

    def _insert_missing_products(self, products_by_status: dict) -> list[tuple[int, str]]:
        inserted_products = []
        try:
            cur = self.conn.cursor()
            for status, products in products_by_status.items():
                if products:
                    ids = execute_values(cur, """
                        INSERT INTO csaf_products (cpe, package, module)
                        VALUES %s returning id;
                        """, (products), fetch=True)
                    inserted_products.extend([(result[0], status) for result in ids])
                self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            self.logger.exception("Failure while inserting data into csaf_products: %s", exc)
            self.conn.rollback()
        finally:
            cur.close()

        return inserted_products

    def _insert_cves(self, cve, products):
        try:
            cur = self.conn.cursor()
            if products:
                execute_values(cur, """
                    INSERT INTO csaf_cves (cve, csaf_product_id, product_status_id)
                    VALUES %s
                    ON CONFLICT (cve, csaf_product_id)
                    DO UPDATE SET product_status_id = EXCLUDED.product_status_id;
                    """, [(cve, product[0], product[1]) for product in products])
                self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            CSAF_FAILED_UPDATE.inc()
            self.logger.exception("Failure while inserting or updating data to csaf_cves: %s", exc)
            self.conn.rollback()
        finally:
            cur.close()

    def _remove_cves(self, cve, ids):
        if not ids:
            return
        try:
            cur = self.conn.cursor()
            cur.execute("""DELETE FROM csaf_cves WHERE cve = %s and csaf_product_id not in %s""",
                        (cve, tuple(row[1] for row in ids)))
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("Failure while removing data from csaf cves: %s", exc)
            self.conn.rollback()
        finally:
            cur.close()

    def _map_products_by_status(self, products) -> dict[int, list[tuple[str, str, str]]]:
        products_by_status = defaultdict(list)

        for product in products:
            status_id = product[2]
            product_data = (product[0], product[1], product[3])
            products_by_status[status_id].append(product_data)

        return products_by_status

    def _populate_cves(self, csaf_cves: CsafCves):
        for cve in csaf_cves.keys():
            cve_products = csaf_cves.to_tuples(cve, ("cpe", "package", "status_id", "module"))
            products = self._map_products_by_status(cve_products)
            to_insert, to_associate_ids = self._get_product_rows(products)
            inserted_ids = self._insert_missing_products(to_insert)
            all_ids = to_associate_ids+inserted_ids
            self._remove_cves(cve, all_ids)
            self._insert_cves(cve, all_ids)

    def _delete_unreferenced_products(self):
        try:
            cur = self.conn.cursor()
            cur.execute("""DELETE FROM csaf_products
                            WHERE id IN (
                                SELECT p.id
                                FROM csaf_products AS p
                                LEFT JOIN csaf_cves AS c ON c.csaf_product_id = p.id
                                WHERE c.csaf_product_id IS NULL)""")
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("Failure while deleting data from csaf_products: %s", exc)
            self.conn.rollback()
        finally:
            cur.close()

    def store(self, csaf_data: CsafData):
        """Store collection of CSAF files into DB."""
        self._save_csaf_files(csaf_data.files)
        self._populate_cves(csaf_data.cves)
        self._delete_unreferenced_products()
