"""
Module containing database handler class.
"""
import os
import psycopg2


class NamedCursor:
    """Wrapper class for named cursor."""
    def __init__(self, db_connection, name="default"):
        self.cursor = db_connection.cursor(name=name)

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()

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

    @classmethod
    def rollback(cls):
        """Rollback any pending transaction."""
        if cls.connection is not None:
            cls.connection.rollback()

def init_db():
    """Setup DB connection parameters"""
    DatabaseHandler.db_name = os.getenv('POSTGRESQL_DATABASE', "vmaas")
    DatabaseHandler.db_user = os.getenv('POSTGRESQL_USER', "vmaas_writer")
    DatabaseHandler.db_pass = os.getenv('POSTGRESQL_PASSWORD', "vmaas_writer_passwd")
    DatabaseHandler.db_host = os.getenv('POSTGRESQL_HOST', "database")
    DatabaseHandler.db_port = int(os.getenv('POSTGRESQL_PORT', "5432"))
