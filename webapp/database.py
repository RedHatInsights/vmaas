import os
import psycopg2

def _set_val(value, envname, default):
    return value if value is not None else os.getenv(envname, default)

class Database:
    DEFAULT_NAME = "vmaas"
    DEFAULT_USER = "vmaas_user"
    DEFAULT_PASSWORD = "vmaas_passwd"
    DEFAULT_HOST = "vmaas-database"
    DEFAULT_PORT = 5432

    def __init__(self, db_name=None, db_user=None, db_pass=None, db_host=None, db_port=None):
        self.name = _set_val(db_name, 'POSTGRESQL_DATABASE', self.DEFAULT_NAME)
        self.user = _set_val(db_user, 'POSTGRESQL_USER', self.DEFAULT_USER)
        self.password = _set_val(db_pass, 'POSTGRESQL_PASSWORD', self.DEFAULT_PASSWORD)
        self.host = _set_val(db_host, 'POSTGRESQL_HOST', self.DEFAULT_HOST)
        self.port = _set_val(db_port, 'POSTGRESQL_PORT', self.DEFAULT_PORT)

        self.connection=psycopg2.connect(database=self.name,
                                         user=self.user,
                                         password=self.password,
                                         host=self.host,
                                         port=self.port)
        self.connection.set_session(readonly=True, autocommit=True)

    def cursor(self):
        return self.connection.cursor()
