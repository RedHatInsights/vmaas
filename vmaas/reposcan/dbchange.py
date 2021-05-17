"""
Dbchange API implementation.
"""
from vmaas.reposcan.database.database_handler import DatabaseHandler, init_db


class DbChangeAPI:
    """API class to work with dbchange. """
    db_instance = None

    def process(self):
        """Processes the dbchange get request. """
        init_db()
        self.db_instance = DatabaseHandler.get_connection()
        result = {}

        with self.db_instance.cursor() as crs:
            crs.execute("select pkgtree_change from dbchange")
            timestamp = crs.fetchone()

        result["pkgtree_change"] = str(timestamp[0])
        return result
