"""
Module containing classes for fetching/importing products from/into database.
"""
from psycopg2.extras import execute_values

from common.logging_utils import get_logger
from database.database_handler import DatabaseHandler


class ProductStore:
    """
    Class providing interface for storing product info.
    """
    def __init__(self):
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()

    def _import_products(self, products):
        product_to_dbid = {}
        self.logger.debug("Syncing %d products.", len(products))
        cur = self.conn.cursor()
        try:
            cur.execute("select id, name from product where name in %s",
                        (tuple(products.keys()),))
            for row in cur.fetchall():
                product_to_dbid[row[1]] = row[0]
            missing_products = []
            for product in products:
                if product not in product_to_dbid:
                    missing_products.append((products[product]["product_id"], product))
            self.logger.debug("Products already in DB: %d", len(product_to_dbid))
            self.logger.debug("Products to import: %d", len(missing_products))
            if missing_products:
                execute_values(cur, """insert into product (redhat_eng_product_id, name) values %s
                                       on conflict (redhat_eng_product_id) do update set name = excluded.name
                                       returning id, name""", missing_products,
                               page_size=len(missing_products))
                for row in cur.fetchall():
                    product_to_dbid[row[1]] = row[0]
            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failure inserting into product.")
            self.conn.rollback()
        finally:
            cur.close()
        return product_to_dbid

    def _import_content_sets(self, products):
        product_to_dbid = self._import_products(products)
        if product_to_dbid: # pylint: disable=too-many-nested-blocks
            all_content_set_labels = [cs for product in products.values() for cs in product["content_sets"]]
            self.logger.debug("Syncing %d content sets.", len(all_content_set_labels))
            cs_to_dbid = {}
            cur = self.conn.cursor()
            try:
                cur.execute("select id, label from content_set where label in %s", (tuple(all_content_set_labels),))
                for row in cur.fetchall():
                    cs_to_dbid[row[1]] = row[0]
                missing_content_sets = []
                for product in products:
                    for content_set in products[product]["content_sets"]:
                        if content_set not in cs_to_dbid:
                            # label, name, product_id
                            missing_content_sets.append((content_set, products[product]["content_sets"][content_set],
                                                         product_to_dbid[product]))
                self.logger.debug("Content sets already in DB: %d", len(cs_to_dbid))
                self.logger.debug("Content sets to import: %d", len(missing_content_sets))
                if missing_content_sets:
                    execute_values(cur, """insert into content_set (label, name, product_id) values %s
                                           returning id, label""",
                                   missing_content_sets, page_size=len(missing_content_sets))
                    for row in cur.fetchall():
                        cs_to_dbid[row[1]] = row[0]
                self.conn.commit()
            except Exception:  # pylint: disable=broad-except
                self.logger.exception("Failed to insert into content_set.")
                self.conn.rollback()
            finally:
                cur.close()

    def store(self, products):
        """
        Import all product info from input dictionary.
        """
        self._import_content_sets(products)
