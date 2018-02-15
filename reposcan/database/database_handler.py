"""
Module containing database handler class.
"""
import psycopg2


class DatabaseHandler:
    """Static class maintaining single PostgreSQL connection."""
    db_name = None
    db_user = None
    db_pass = None
    db_host = None
    db_port = None
    connection = None

    @classmethod
    def get_connection(cls):
        """Get database connection. Create new connection if doesn't exist."""
        if cls.connection is None:
            cls.connection = psycopg2.connect(
                database=cls.db_name, user=cls.db_user, password=cls.db_pass, host=cls.db_host, port=cls.db_port)
        return cls.connection

    @classmethod
    def close_connection(cls):
        """Close database connection."""
        if cls.connection is not None:
            cls.connection.close()
            cls.connection = None
