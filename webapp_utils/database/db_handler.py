"""
Module for connecting and working with vmaas database.
"""
import os
from psycopg2 import pool


VMAAS_DB_LOGIN = os.getenv("POSTGRESQL_USER", None)
VMAAS_DB_PASSWD = os.getenv("POSTGRESQL_PASSWORD", None)
VMAAS_DB_NAME = os.getenv("POSTGRESQL_DATABASE", None)
VMAAS_DB_HOST = os.getenv("POSTGRESQL_HOST", None)
VMAAS_DB_PORT = os.getenv("POSTGRESQL_PORT", None)

class DatabasePoolConnection:
    """ Wrapper for psycopg2 one connection pool from DatabasePoolHandler. """
    def __init__(self, conn):
        self.conn = conn

    def get_cursor(self):
        """ Gets one cursor based on connection from pool. """
        return self.conn.cursor()

class DatabasePoolHandler:
    """ Handler class for pool connection into db and querying. """

    def __init__(self, size, dsn=None):
        if dsn:
            self.db_pool = pool.ThreadedConnectionPool(1, size,
                                                       dbname=dsn["database"], user=dsn["user"],
                                                       host=dsn["host"], port=dsn["port"])
        else:
            self.db_pool = pool.ThreadedConnectionPool(1, size,
                                                       dbname=VMAAS_DB_NAME, user=VMAAS_DB_LOGIN,
                                                       password=VMAAS_DB_PASSWD,
                                                       host=VMAAS_DB_HOST, port=VMAAS_DB_PORT)

    def get_connection(self):
        """ Gets one connection from pool. """
        return DatabasePoolConnection(self.db_pool.getconn())

    def return_connection(self, conn):
        """ Returns one connection back to the database pool. """
        self.db_pool.putconn(conn.conn)
