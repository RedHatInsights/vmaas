"""Pytest configuration for database tests."""

import os

from pathlib import Path
import psycopg2
import pytest
import testing.postgresql

from vmaas.reposcan.database.database_handler import init_db

TEST_DIR = Path(__file__).resolve().parent
REPOSCAN_DIR = (TEST_DIR.parent).parent
VMAAS_DIR = (REPOSCAN_DIR.parent).parent
VMAAS_DB_DIR = VMAAS_DIR.joinpath("database")

VMAAS_PG = VMAAS_DB_DIR.joinpath("vmaas_db_postgresql.sql")
VMAAS_USER = VMAAS_DB_DIR.joinpath("vmaas_user_create_postgresql.sql")

os.environ["POSTGRESQL_DATABASE"] = "test"
os.environ["POSTGRESQL_HOST"] = "127.0.0.1"
os.environ["POSTGRESQL_PASSWORD"] = ""


@pytest.fixture(scope="session")
def db_conn():
    """Fixture for db connection."""
    postgresql = create_pg()
    init_db()
    conn = psycopg2.connect(**postgresql.dsn())
    yield conn

    # teardown - close connection, stop postgresql
    conn.close()
    postgresql.stop()


def create_pg(vmaas_user=VMAAS_USER, vmaas_pg=VMAAS_PG):
    """ Create postgres instance with given SQL scripts. """
    def _handler(postgresql):
        """ Handler which intializes scheme in instance. """
        conn = psycopg2.connect(**postgresql.dsn())

        with conn.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
            cursor.execute("GRANT ALL ON SCHEMA public TO postgres")
            cursor.execute("GRANT ALL ON SCHEMA public TO public")

        with conn.cursor() as cursor:
            cursor.execute(vmaas_user.read_text(encoding="utf-8"))
            cursor.execute(vmaas_pg.read_text(encoding="utf-8"))

        conn.commit()
        conn.close()

    # pylint: disable=invalid-name
    Postgresql = testing.postgresql.PostgresqlFactory(
        cache_initialized_db=True,
        on_initialized=_handler,
    )
    postgresql = Postgresql()
    os.environ["POSTGRESQL_PORT"] = str(postgresql.dsn()["port"])

    return postgresql
