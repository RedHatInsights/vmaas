"""
Module containing classes for fetching/importing CSAF data from/into database.
"""
from psycopg2.extras import execute_values

from vmaas.reposcan.database.object_store import ObjectStore
from vmaas.reposcan.mnm import CSAF_FAILED_DELETE
from vmaas.reposcan.redhatcsaf.modeling import CsafData
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

    def store(self, csaf_data: CsafData):
        """Store collection of CSAF files into DB."""
        self._save_csaf_files(csaf_data.files)
        # TODO: populate future objects in csaf store
