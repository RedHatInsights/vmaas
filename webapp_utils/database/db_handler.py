"""
Module for connecting and working with vmaas database.
"""
from psycopg2 import pool

from common.config import Config


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
            cfg = Config()
            self.db_pool = pool.ThreadedConnectionPool(1, size,
                                                       dbname=cfg.db_name, user=cfg.db_user,
                                                       password=cfg.db_pass,
                                                       host=cfg.db_host, port=cfg.db_port)

    def get_connection(self):
        """ Gets one connection from pool. """
        return DatabasePoolConnection(self.db_pool.getconn())

    def return_connection(self, conn):
        """ Returns one connection back to the database pool. """
        self.db_pool.putconn(conn.conn)
