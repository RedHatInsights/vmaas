"""
Dummy database creator used for testing.
"""
import testing.postgresql
import psycopg2


DB_SCHEMA = open("../database/vmaas_db_postgresql.sql", "r").read()
DB_USERS = open("../database/vmaas_user_create_postgresql.sql", "r").read()
DUMMY_DATA = open("test/db/dummy_data.sql").read()

class DummyDatabase():
    """ Class for the dummy database which creates vmaas database dummy copy,
        based on the schema sql files. """
    def __init__(self):
        self.database = testing.postgresql.Postgresql()
        conn = psycopg2.connect(**self.database.dsn())

        with conn.cursor() as cursor:
            cursor.execute(DB_USERS)
            cursor.execute(DB_SCHEMA)
            cursor.execute(DUMMY_DATA)

        conn.commit()
        conn.close()
