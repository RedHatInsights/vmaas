"""
Module containing classes for fetching/importing CSAF data from/into database.
"""
from copy import deepcopy
from typing import Any
from typing import Iterable

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


class CsafStoreRetryCVE(CsafStoreSkippedCVE):
    """CsafStoreRetryCVE exception."""


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
        self.skipped_cve_categories: dict[str, int] = {}

    def delete_csaf_files(self, csaf_files: Iterable[model.CsafFile]) -> None:
        """Delete csaf files from DB."""
        if not csaf_files:
            return

        removed_files = []
        removed_file_names = []
        for csaf_file in csaf_files:
            removed_files.append(csaf_file.id_)
            removed_file_names.append(csaf_file.name)

        if not removed_files:
            return

        cur = self.conn.cursor()
        try:
            cur.execute("delete from csaf_cve_product where csaf_file_id in %s", (tuple(removed_files),))
            cur.execute("delete from csaf_file where id in %s", (tuple(removed_files),))
            self.conn.commit()
            self.logger.info("%d CSAF files removed", len(removed_file_names))
            self.logger.debug("Removed csaf_files: %s", removed_file_names)
        except Exception as exc:
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("%s: ", FAILED_FILE_DELETE)
            self.conn.rollback()
            raise CsafStoreException(FAILED_FILE_DELETE) from exc
        finally:
            cur.close()

    def _save_csaf_files(self, csaf_files: model.CsafFiles) -> None:
        if not csaf_files:
            return

        cur = self.conn.cursor()
        try:
            files = csaf_files.to_tuples(("name",))
            execute_values(
                cur,
                """
                    insert into csaf_file (name) values %s
                    on conflict (name) do nothing
                """,
                files,
            )
            cur.execute("select id, name from csaf_file where name in %s", (tuple(files),))
            rows = cur.fetchall()
            self.conn.commit()
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            self.logger.exception("%s: ", FAILED_FILE_IMPORT)
            raise CsafStoreException(FAILED_FILE_IMPORT) from exc
        finally:
            cur.close()
        for row in rows:
            csaf_files[row[1]].id_ = row[0]
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
            except KeyError:
                self.logger.debug("Inserting missing cpe %s", product.cpe)
                self.cpe_store.populate_cpes({product.cpe: None})
                product.cpe_id = self._get_product_attr_id("cpe", self.cpe_store.cpe_label_to_id, value=product.cpe)
            try:
                match product.status_id:
                    case model.CsafProductStatus.KNOWN_AFFECTED:
                        # product for unfixed cve, we have only package_name
                        product.package_name_id = self._get_product_attr_id(
                            "package_name", self.package_store.package_name_map, value=product.package
                        )
                    case model.CsafProductStatus.FIXED:
                        # parse package into NEVRA
                        name, epoch, ver, rel, arch = rpm.parse_rpm_name(product.package)
                        name_id = self.package_store.package_name_map[name]
                        evr_id = self.package_store.evr_map[(epoch, ver, rel)]
                        arch_id = self.package_store.arch_map[arch]
                        product.package_name_id = name_id
                        product.package_id = self._get_product_attr_id(
                            "package", self.package_store.package_map, value=(name_id, evr_id, arch_id)
                        )
                    case _:
                        raise NotImplementedError(f"Unsupported product_status_id '{product.status_id}'")

                products.add_to_lookup(product)
            except (AttributeError, KeyError, rpm.RPMParseException) as err:
                self.logger.debug("Skipping product %s, %s", product, err)
                skipped.append(product)

        for product in skipped:
            products.remove(product)

    def _set_product_ids(self, rows: list[tuple[Any, ...]], products: model.CsafProducts) -> None:
        for row in rows:
            product = products.get_by_ids_module_variant(
                cpe_id=row[1],
                variant_suffix=row[2],
                package_name_id=row[3],
                package_id=row[4],
                module=row[5],
            )
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
        variant_field = sql.Identifier("variant_suffix")

        fields_unfixed = [cpe_field, variant_field, package_name_field]
        fields_unfixed_module = [cpe_field, variant_field, package_name_field, module_field]
        fields_fixed = [cpe_field, variant_field, package_name_field, package_field]
        fields_fixed_module = [cpe_field, variant_field, package_name_field, package_field, module_field]

        unfixed_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_unfixed_module),
            "module_null": not_null,
            "package_null": null,
        }
        unfixed_no_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_unfixed),
            "module_null": null,
            "package_null": null,
        }
        fixed_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_fixed_module),
            "module_null": not_null,
            "package_null": not_null,
        }
        fixed_no_module = {
            "products": [],
            "fields": sql.SQL(", ").join(fields_fixed),
            "module_null": null,
            "package_null": not_null,
        }

        res = {
            "unfixed_module": unfixed_module,
            "unfixed_no_module": unfixed_no_module,
            "fixed_module": fixed_module,
            "fixed_no_module": fixed_no_module,
        }
        for row in products.to_tuples(("cpe_id", "variant_suffix", "package_name_id", "package_id", "module")):
            if row[0] is None:
                self.logger.error("Missing cpe_id for product %s", row)
                continue

            if any(not isinstance(row[i], (int, str, type(None))) for i in range(4)):
                raise TypeError(f"column of product row <{row}> is not of type (int, str, None)")

            if row[2] and not row[3]:  # unfixed
                if row[4]:  # has module
                    res["unfixed_module"]["products"].append((row[0], row[1], row[2], row[4]))  # type: ignore[attr-defined]
                else:
                    res["unfixed_no_module"]["products"].append((row[0], row[1], row[2]))  # type: ignore[attr-defined]
            elif row[3]:  # fixed
                if row[4]:  # has module
                    res["fixed_module"]["products"].append((row[0], row[1], row[2], row[3], row[4]))  # type: ignore[attr-defined]
                else:
                    res["fixed_no_module"]["products"].append((row[0], row[1], row[2], row[3]))  # type: ignore[attr-defined]
        return res

    def _update_product_ids(self, products: model.CsafProducts) -> None:
        if not products:
            return

        all_rows = []
        query = sql.SQL(
            """
            SELECT id, cpe_id, variant_suffix, package_name_id, package_id, module_stream
            FROM csaf_product
            WHERE ({fields}) in %s
                AND module_stream IS {module_null}
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
                    INSERT INTO csaf_product (cpe_id, variant_suffix, package_name_id, package_id, module_stream)
                    VALUES %s
                    RETURNING id, cpe_id, variant_suffix, package_name_id, package_id, module_stream
                """,
                products.to_tuples(
                    ("cpe_id", "variant_suffix", "package_name_id", "package_id", "module"),
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
                raise CsafStoreRetryCVE(f"{cve} not found in DB")

            file_id = self.cve2file_id[cve]
            to_upsert = [
                (row[0], id_, status_id, file_id, erratum)
                for id_, status_id, erratum in products.to_tuples(("id_", "status_id", "erratum"), with_id=True)
            ]
            execute_values(
                cur,
                """
                    INSERT INTO csaf_cve_product (cve_id, csaf_product_id, csaf_product_status_id, csaf_file_id, erratum)
                    VALUES %s
                    ON CONFLICT (cve_id, csaf_product_id)
                    DO UPDATE SET csaf_product_status_id = EXCLUDED.csaf_product_status_id, erratum = EXCLUDED.erratum
                """,
                to_upsert,
            )
            self.conn.commit()
        except CsafStoreRetryCVE as exc:
            raise exc
        except Exception as exc:
            CSAF_FAILED_IMPORT.inc()
            CSAF_FAILED_UPDATE.inc()
            self.logger.exception("%s: ", FAILED_CVE_UPSERT)
            self.conn.rollback()
            raise CsafStoreException(FAILED_CVE_UPSERT) from exc
        finally:
            cur.close()

    def _remove_cves(self, cve: str, products: model.CsafProducts) -> None:
        cur = self.conn.cursor()
        q_inner = "DELETE FROM csaf_cve_product ccp USING cve WHERE {} RETURNING *"
        q_where_all = "ccp.cve_id = cve.id AND cve.name = %s"
        q_where_not_in = f"{q_where_all} AND csaf_product_id NOT IN %s"
        query = f"WITH del AS ({q_inner}) SELECT count(*) FROM del"
        if products:
            query_params = (cve, tuple(x.id_ for x in products))
            query = query.format(q_where_not_in)
        else:
            # remove all products associated with the CVE
            query_params = (cve,)  # type: ignore[assignment]
            query = query.format(q_where_all)

        try:
            cur.execute(query, query_params)
            res = cur.fetchone()
            self.conn.commit()
            if res and len(res) > 0:
                self.logger.debug("Deleted %d products from %s", res[0], cve)
        except Exception as exc:
            CSAF_FAILED_DELETE.inc()
            self.logger.exception("%s: ", FAILED_CVE_DELETE)
            self.conn.rollback()
            raise CsafStoreException(FAILED_CVE_DELETE) from exc
        finally:
            cur.close()

    def _update_file_timestamp(self, cve: str, files: model.CsafFiles) -> None:
        cur = self.conn.cursor()
        try:
            file_id = self.cve2file_id[cve]
            csaf_file = files.get_by_id(file_id)
            if csaf_file is None:
                raise CsafStoreException(f"csaf_file with id={file_id} not found")
            cur.execute("UPDATE csaf_file SET updated = %s WHERE id = %s", (csaf_file.csv_timestamp, file_id))
            self.conn.commit()
        except Exception as exc:
            raise CsafStoreException(f"failed to update csaf_file for {cve}") from exc
        finally:
            cur.close()

    def _populate_cves(self, csaf_cves: model.CsafCves, files: model.CsafFiles) -> None:
        for cve, products in csaf_cves.items():
            products_copy = deepcopy(products)  # only for logging of failed cves
            try:
                self._update_product_ids(products)
                self._insert_missing_products(products)
                self._remove_cves(cve, products)
                self._insert_cves(cve, products)
                self._update_file_timestamp(cve, files)
            except CsafStoreRetryCVE as exc:
                self._categorize_skipped_cves(exc)
                self.logger.debug("Skipping cve: %s products: %s reason: %s", cve, products_copy, exc)
            except CsafStoreSkippedCVE as exc:
                self._categorize_skipped_cves(exc)
                self.logger.debug("Skipping cve: %s products: %s reason: %s", cve, products_copy, exc)
                self._update_file_timestamp(cve, files)
            except CsafStoreException:
                self.logger.exception("Failed to populate cve: %s products: %s ", cve, products_copy)
        self.logger.warning("Skipped cves: %s", self.skipped_cve_categories)

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

    def _categorize_skipped_cves(self, exc: Exception) -> None:
        if str(exc) not in self.skipped_cve_categories:
            self.skipped_cve_categories[str(exc)] = 0
        self.skipped_cve_categories[str(exc)] += 1

    def store(self, csaf_data: model.CsafData) -> None:
        """Store collection of CSAF files into DB."""
        if not csaf_data:
            self.logger.warning("CsafData without cves or files")
            return

        self._save_csaf_files(csaf_data.files)
        self._populate_cves(csaf_data.cves, csaf_data.files)
        self._delete_unreferenced_products()
