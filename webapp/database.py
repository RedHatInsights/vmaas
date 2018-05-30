"""
Module to handle database connections.
"""
import os
import psycopg2
import psycopg2.extras

def _set_val(value, envname, default):
    return value if value is not None else os.getenv(envname, default)

class Database(object):
    """ Database handler class. """
    DEFAULT_NAME = "vmaas"
    DEFAULT_USER = "vmaas_reader"
    DEFAULT_PASSWORD = "vmaas_reader_pwd"
    DEFAULT_HOST = "vmaas-database"
    DEFAULT_PORT = 5432

    def __init__(self, db_name=None, db_user=None, db_pass=None, db_host=None, db_port=None):
        self.name = _set_val(db_name, 'POSTGRESQL_DATABASE', self.DEFAULT_NAME)
        self.user = _set_val(db_user, 'POSTGRESQL_USER', self.DEFAULT_USER)
        self.password = _set_val(db_pass, 'POSTGRESQL_PASSWORD', self.DEFAULT_PASSWORD)
        self.host = _set_val(db_host, 'POSTGRESQL_HOST', self.DEFAULT_HOST)
        self.port = _set_val(db_port, 'POSTGRESQL_PORT', self.DEFAULT_PORT)

        self.connection = psycopg2.connect(database=self.name,
                                           user=self.user,
                                           password=self.password,
                                           host=self.host,
                                           port=self.port)
        self.connection.set_session(readonly=True)

    def cursor(self, name=None):
        """ Returns cursor object connected to the database."""
        return self.connection.cursor(name=name)

    def dictcursor(self):
        """
        Returns cursor object connected to the database that returns dictionary.
        """
        return self.connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)


class NamedCursor(object):
    """Wrapper class for named cursor."""
    def __init__(self, db_connection, name="default"):
        self.cursor = db_connection.cursor(name=name)

    def __enter__(self):
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
