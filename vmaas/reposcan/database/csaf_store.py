"""
Module containing classes for fetching/importing CSAF data from/into database.
"""
from copy import deepcopy
from typing import Any

from psycopg2 import sql
from psycopg2.extras import execute_values

import vmaas.common.rpm_utils as rpm
from vmaas.reposcan.database.cpe_store import CpeStore
from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.reposcan.database.package_store import PackageStore
from vmaas.reposcan.mnm import CSAF_FAILED_DELETE
from vmaas.reposcan.mnm import CSAF_FAILED_IMPORT
from vmaas.reposcan.mnm import CSAF_FAILED_UPDATE
from vmaas.reposcan.redhatcsaf import modeling as model

FAILED_FILE_DELETE = "Failure while deleting CSAF file"
FAILED_FILE_IMPORT = "Failed to import csaf file to DB"
FAILED_PRODUCT_FETCH = "Failure while fetching CSAF products from the DB"
FAILED_PRODUCT_INSERT = "Failure while inserting data into csaf_product"
FAILED_CVE_UPSERT = "Failure while inserting or updating data to csaf_cves"
FAILED_CVE_DELETE = "Failure while removing data from csaf cves"
FAILED_PRODUCT_DELETE = "Failure while deleting data from csaf_product"


class CsafStoreException(Exception):
    """CsafStoreException exception."""


class CsafStoreSkippedCVE(CsafStoreException):
    """CsafStoreSkippedCVE exception."""


class CsafStore(ObjectStore):
    """Class providing interface for fetching/importing CSAF data from/into the DB."""

    def __init__(self) -> None:
        super().__init__()  # type: ignore[no-untyped-call]
        self.cpe_store = CpeStore()  # type: ignore[no-untyped-call]
        self.package_store = PackageStore()  # type: ignore[no-untyped-call]
        self.csaf_file_map: dict[str, tuple[int, str]] = self._prepare_table_map(  # type: ignore[assignment]
            cols=("name",), to_cols=("id", "updated"), table="csaf_file"
        )
        self.cve2file_id: dict[str, int] = {}

    def delete_csaf_file(self, name: str) -> None:
        """Deletes csaf file from DB."""
        db_id = self.csaf_file_map[name][0]
        cur = self.conn.cursor()
        try:
            cur.execute("delete from csaf_file where id = %s", (db_id,))
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("%s: ", FAILED_FILE_DELETE)
            self.conn.rollback()
            raise CsafStoreException(FAILED_FILE_DELETE) from exc
        finally:
            cur.close()

    def _save_csaf_files(self, csaf_files: model.CsafFiles) -> None:
        cur = self.conn.cursor()
        try:
            rows = execute_values(
                cur,
                """
                    insert into csaf_file (name, updated) values %s
                    on conflict (name) do update set updated = excluded.updated
                    returning id, name
                """,
                csaf_files.to_tuples(("name", "csv_timestamp")),
                fetch=True,
            )
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            self.logger.exception("%s: ", FAILED_FILE_IMPORT)
            raise CsafStoreException(FAILED_FILE_IMPORT) from exc
        finally:
            cur.close()
        for row in rows:
            file_cves = csaf_files[row[1]].cves
            if not file_cves:
                self.logger.warning("File %s not associated with any CVEs", row[1])
                continue
            for cve in file_cves:
                self.cve2file_id[cve] = row[0]

    def _get_product_attr_id(  # type: ignore[return]
        self, attr_type: str, mapping: dict[str, int] | dict[tuple[str, ...], int], value: str | tuple[str, ...]
    ) -> int:
        try:
            return mapping[value]  # type: ignore[index]
        except KeyError as err:
            raise KeyError(f"missing {attr_type}={value}") from err

    def _load_product_attr_ids(self, products: model.CsafProducts) -> None:
        skipped = []
        for product in products:
            try:
                product.cpe_id = self._get_product_attr_id("cpe", self.cpe_store.cpe_label_to_id, value=product.cpe)
                if product.status_id == model.CsafProductStatus.KNOWN_AFFECTED:
                    # product for unfixed cve, we have only package_name
                    product.package_name_id = self._get_product_attr_id(
                        "package_name", self.package_store.package_name_map, value=product.package
                    )
                else:
                    # parse package into NEVRA
                    try:
                        name, epoch, ver, rel, arch = rpm.parse_rpm_name(product.package)
                        name_id = self.package_store.package_name_map[name]
                        evr_id = self.package_store.evr_map[(epoch, ver, rel)]
                        arch_id = self.package_store.arch_map[arch]
                        product.package_id = self._get_product_attr_id(
                            "package", self.package_store.package_map, value=(name_id, evr_id, arch_id)
                        )
                    except rpm.RPMParseException as err:
                        self.logger.debug("Skipping product %s, %s", product, err)
                        skipped.append(product)
                        continue

                products.add_to_lookup(product)
            except (AttributeError, KeyError) as err:
                self.logger.debug("Skipping product %s, %s", product, err)
                skipped.append(product)

        for product in skipped:
            products.remove(product)

    def _set_product_ids(self, rows: list[tuple[Any, ...]], products: model.CsafProducts) -> None:
        for row in rows:
            product = products.get_by_ids_and_module(row[1], row[2], row[3], row[4])
            if product is None:
                # log as error, this would be a programming error
                self.logger.error("Product %s not found in model.CsafProducts lookup", product)
                continue
            product.id_ = row[0]

    def _split_product_data(self, products: model.CsafProducts) -> dict[str, dict[str, object]]:
        null = sql.SQL("NULL")
        not_null = sql.SQL("NOT NULL")
        cpe_field = sql.Identifier("cpe_id")
        module_field = sql.Identifier("module_stream")
        package_name_field = sql.Identifier("package_name_id")
        package_field = sql.Identifier("package_id")

        fields_unfixed = [cpe_field, package_name_field]
        fields_unfixed_module = [cpe_field, package_name_field, module_field]
        fields_fixed = [cpe_field, package_field]
        fields_fixed_module = [cpe_field, package_field, module_field]

        unfixed_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_unfixed_module),
            "module_null": not_null,
            "package_name_null": not_null,
            "package_null": null,
        }
        unfixed_no_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_unfixed),
            "module_null": null,
            "package_name_null": not_null,
            "package_null": null,
        }
        fixed_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_fixed_module),
            "module_null": not_null,
            "package_name_null": null,
            "package_null": not_null,
        }
        fixed_no_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_fixed),
            "module_null": null,
            "package_name_null": null,
            "package_null": not_null,
        }

        res = {
            "unfixed_module": unfixed_module,
            "unfixed_no_module": unfixed_no_module,
            "fixed_module": fixed_module,
            "fixed_no_module": fixed_no_module,
        }
        for row in products.to_tuples(("cpe_id", "package_name_id", "package_id", "module")):
            if row[0] is None:
                self.logger.error("Missing cpe_id for product %s", row)
                continue

            if any(not isinstance(row[i], (int, str, type(None))) for i in range(4)):
                raise TypeError(f"column of product row <{row}> is not of type (int, str, None)")

            if row[1]:  # unfixed
                if row[3]:  # has module
                    res["unfixed_module"]["products"].append((row[0], row[1], row[3]))  # type: ignore[attr-defined]
                else:
                    res["unfixed_no_module"]["products"].append((row[0], row[1]))  # type: ignore[attr-defined]
            elif row[2]:  # fixed
                if row[3]:  # has module
                    res["fixed_module"]["products"].append((row[0], row[2], row[3]))  # type: ignore[attr-defined]
                else:
                    res["fixed_no_module"]["products"].append((row[0], row[2]))  # type: ignore[attr-defined]
        return res

    def _update_product_ids(self, products: model.CsafProducts) -> None:
        if not products:
            return

        all_rows = []
        query = sql.SQL(
            """
            SELECT id, cpe_id, package_name_id, package_id, module_stream
            FROM csaf_product
            WHERE ({fields}) in %s
                AND module_stream IS {module_null}
                AND package_name_id IS {package_name_null}
                AND package_id IS {package_null}
            """
        )
        cur = self.conn.cursor()
        try:
            self._load_product_attr_ids(products)

            for key, val in self._split_product_data(products).items():
                self.logger.debug("loading <%s> products", key)
                product_tuples: tuple[tuple[int | str, ...]] = tuple(val["products"])  # type: ignore
                if product_tuples:
                    formatted_query = query.format(
                        fields=val["fields"],  # type: ignore[arg-type]
                        module_null=val["module_null"],  # type: ignore[arg-type]
                        package_name_null=val["package_name_null"],  # type: ignore[arg-type]
                        package_null=val["package_null"],  # type: ignore[arg-type]
                    )
                    cur.execute(formatted_query, (product_tuples,))
                    rows = cur.fetchall()
                    all_rows.extend(rows)

            self._set_product_ids(all_rows, products)
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            self.logger.exception("%s: ", FAILED_PRODUCT_FETCH)
            raise CsafStoreException(FAILED_PRODUCT_FETCH) from exc
        finally:
            cur.close()

    def _insert_missing_products(self, products: model.CsafProducts) -> None:
        if not products:
            return

        cur = self.conn.cursor()
        try:
            rows = execute_values(
                cur,
                """
                    INSERT INTO csaf_product (cpe_id, package_name_id, package_id, module_stream)
                    VALUES %s
                    RETURNING id, cpe_id, package_name_id, package_id, module_stream
                """,
                products.to_tuples(
                    ("cpe_id", "package_name_id", "package_id", "module"),
                    missing_only=True,
                    with_cpe_id=True,
                    with_pkg_id=True,
                ),
                fetch=True,
            )
            self.conn.commit()
            self._set_product_ids(rows, products)
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            self.logger.exception("%s: ", FAILED_PRODUCT_INSERT)
            self.conn.rollback()
            raise CsafStoreException(FAILED_PRODUCT_INSERT) from exc
        finally:
            cur.close()

    def _insert_cves(self, cve: str, products: model.CsafProducts) -> None:
        if not products:
            raise CsafStoreSkippedCVE("cannot map any products")

        cur = self.conn.cursor()
        try:
            cur.execute("SELECT id FROM cve WHERE UPPER(name) = %s", (cve,))
            if (row := cur.fetchone()) is None:
                raise CsafStoreException(f"{cve} not found in DB")

            file_id = self.cve2file_id[cve]
            to_upsert = [
                (row[0], id_, status_id, file_id)
                for id_, status_id in products.to_tuples(("id_", "status_id"), with_id=True)
            ]
            execute_values(
                cur,
                """
                    INSERT INTO csaf_cve_product (cve_id, csaf_product_id, csaf_product_status_id, csaf_file_id)
                    VALUES %s
                    ON CONFLICT (cve_id, csaf_product_id)
                    DO UPDATE SET csaf_product_status_id = EXCLUDED.csaf_product_status_id
                """,
                to_upsert,
            )
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            CSAF_FAILED_UPDATE.inc()
            self.logger.exception("%s: ", FAILED_CVE_UPSERT)
            self.conn.rollback()
            raise CsafStoreException(FAILED_CVE_UPSERT) from exc
        finally:
            cur.close()

    def _remove_cves(self, cve: str, products: model.CsafProducts) -> None:
        if not products:
            return

        cur = self.conn.cursor()
        try:
            cur.execute(
                """
                    DELETE FROM csaf_cve_product ccp
                    USING cve
                    WHERE ccp.cve_id = cve.id
                        AND cve.name = %s
                        AND csaf_product_id NOT IN %s
                """,
                (cve, tuple(x.id_ for x in products)),
            )
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("%s: ", FAILED_CVE_DELETE)
            self.conn.rollback()
            raise CsafStoreException(FAILED_CVE_DELETE) from exc
        finally:
            cur.close()

    def _populate_cves(self, csaf_cves: model.CsafCves) -> None:
        for cve, products in csaf_cves.items():
            products_copy = deepcopy(products)  # only for logging of failed cves
            try:
                self._update_product_ids(products)
                self._insert_missing_products(products)
                self._remove_cves(cve, products)
                self._insert_cves(cve, products)
            except CsafStoreSkippedCVE as exc:
                self.logger.warning("Skipping cve: %s reason: %s", cve, exc)
                self.logger.debug("Skipping cve: %s products: %s reason: %s", cve, products_copy, exc)
            except CsafStoreException:
                self.logger.exception("Failed to populate cve: %s products: %s ", cve, products_copy)

    def _delete_unreferenced_products(self) -> None:
        cur = self.conn.cursor()
        try:
            cur.execute(
                """DELETE FROM csaf_product
                            WHERE id IN (
                                SELECT p.id
                                FROM csaf_product AS p
                                LEFT JOIN csaf_cve_product AS c ON c.csaf_product_id = p.id
                                WHERE c.csaf_product_id IS NULL)"""
            )
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("%s: ", FAILED_PRODUCT_DELETE)
            self.conn.rollback()
            raise CsafStoreException(FAILED_PRODUCT_DELETE) from exc
        finally:
            cur.close()

    def store(self, csaf_data: model.CsafData) -> None:
        """Store collection of CSAF files into DB."""
        self._save_csaf_files(csaf_data.files)
        self._populate_cves(csaf_data.cves)
        self._delete_unreferenced_products()
