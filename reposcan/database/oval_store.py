"""
Module containing classes for fetching/importing OVAL data from/into database.
"""
from common.dateutil import format_datetime, parse_datetime
from common.logging_utils import get_logger
from database.database_handler import DatabaseHandler


class OvalStore:
    """
    Class providing interface for fetching/importing OVAL data from/into the DB.
    """
    OVAL_FEED_UPDATED_KEY = 'redhatovalfeed:updated'

    def __init__(self):
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()

    def list_oval_definitions(self):
        """List oval definitions and their timestamps stored in DB. Dictionary with oval id as key is returned."""
        cur = self.conn.cursor()
        cur.execute("""select key, value from metadata where key like 'oval:/%%:updated'""")
        return {key: parse_datetime(value) for key, value in cur.fetchall()}

    def save_lastmodified(self, lastmodified, key):
        """Store OVAL file timestamp."""
        lastmodified = format_datetime(lastmodified)
        cur = self.conn.cursor()
        # Update timestamp
        cur.execute("update metadata set value = %s where key = %s",
                    (lastmodified, key,))
        if cur.rowcount < 1:
            cur.execute("insert into metadata (key, value) values (%s, %s)",
                        (key, lastmodified))
        cur.close()
        self.conn.commit()

    def store(self, definitions):
        """Store single OVAL definitions file into DB."""
        self.save_lastmodified(definitions.lastmodified, f"{definitions.oval_id}:updated")
