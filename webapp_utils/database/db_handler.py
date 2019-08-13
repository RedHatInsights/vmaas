"""
Module for connecting and working with vmaas database.
"""
import os
from psycopg2 import pool


VMAAS_DB_LOGIN = os.getenv("POSTGRESQL_USER", None)
VMAAS_DB_PASSWD = os.getenv("POSTGRESQL_PASSWORD", None)
VMAAS_DB_NAME = os.getenv("POSTGRESQL_DATABASE", None)
VMAAS_DB_HOST = os.getenv("POSTGRESQL_HOST", None)
VMAAS_DB_PORT = os.getenv("POSTGRESQL_PORT", 5432)

class CursorWrap:
    """ Wrapper for psycopg2 cursor created by one DatbasePoolConnection. """

    def __init__(self, cursor):
        self.cursor = cursor

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()

class DatabasePoolConnection:
    """ Wrapper for psycopg2 one connection pool from DatabasePoolHandler. """
    def __init__(self, conn):
        self.conn = conn

    def get_cursor(self):
        """ Gets one cursor based on connection from pool. """
        return CursorWrap(self.conn.cursor())

class DatabasePoolHandler:
    """ Handler class for pool connection into db and querying. """

    def __init__(self, size):
        self.db_pool = pool.ThreadedConnectionPool(1, size,
                                                   dbname=VMAAS_DB_NAME, user=VMAAS_DB_LOGIN, password=VMAAS_DB_PASSWD,
                                                   host=VMAAS_DB_HOST, port=VMAAS_DB_PORT)

    def get_connection(self):
        """ Gets one connection from pool. """
        return DatabasePoolConnection(self.db_pool.getconn())
    
    def return_connection(self, conn):
        self.db_pool.putconn(conn.conn)
