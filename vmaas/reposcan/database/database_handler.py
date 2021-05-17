"""
Module containing database handler class.
"""
import os

import psycopg2

from vmaas.common.config import Config


class NamedCursor:
    """Wrapper class for named cursor."""
    def __init__(self, db_connection, name="default"):
        self.cursor = db_connection.cursor(name=name)

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        # NOTE: An exception is raised and passes to the caller
        # if a db exception occurs


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
    """Setup DB connection parameters and initialize DB schema"""
    cfg = Config()
    # allow override by ENV, used in tests and during schema initialization
    DatabaseHandler.db_name = os.getenv("POSTGRESQL_DATABASE", cfg.db_name)
    DatabaseHandler.db_user = os.getenv('POSTGRESQL_USER', cfg.db_user)
    DatabaseHandler.db_pass = os.getenv('POSTGRESQL_PASSWORD', cfg.db_pass)
    DatabaseHandler.db_host = os.getenv("POSTGRESQL_HOST", cfg.db_host)
    DatabaseHandler.db_port = int(os.getenv("POSTGRESQL_PORT", cfg.db_port))
