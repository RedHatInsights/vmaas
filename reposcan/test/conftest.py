"""Pytest configuration for database tests."""

import os

import psycopg2
import pytest
import testing.postgresql

from database.database_handler import init_db, DatabaseHandler

os.environ["POSTGRESQL_DATABASE"] = "test"
os.environ["POSTGRESQL_HOST"] = "127.0.0.1"


@pytest.fixture(scope="module")
def exporter_db_conn():
    """Fixture for db connection."""

    def _handler(postgresql):
        """Init DB with data."""
        conn = psycopg2.connect(**postgresql.dsn())
        cursor = conn.cursor()
        with open("../database/vmaas_user_create_postgresql.sql", "r") as psql_user:
            cursor.execute(psql_user.read())
        with open("../database/vmaas_db_postgresql.sql", "r") as vmaas_db:
            cursor.execute(vmaas_db.read())
        with open("test_data/exporter/exporter_test_data.sql", "r") as test_data:
            cursor.execute(test_data.read())
        cursor.close()
        conn.commit()
        conn.close()

    # Create temporary posgresql server
    # pylint: disable=invalid-name
    Postgresql = testing.postgresql.PostgresqlFactory(
        cache_initialized_db=True, on_initialized=_handler
    )
    postgresql = Postgresql()

    os.environ["POSTGRESQL_PORT"] = str(postgresql.dsn()["port"])
    DatabaseHandler.close_connection()
    init_db()
    conn = psycopg2.connect(**postgresql.dsn())
    yield conn

    # teardown - close connection, stop postgresql
    conn.close()
    postgresql.stop()
