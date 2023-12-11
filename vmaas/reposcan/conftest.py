"""Pytest configuration for database tests."""

import os

from pathlib import Path
import psycopg2
import pytest

from vmaas.common.paths import USER_CREATE_SQL_PATH, DB_CREATE_SQL_PATH
from vmaas.reposcan.database.database_handler import init_db

VMAAS_DIR = Path(__file__).resolve().parent.parent.parent
VMAAS_DB_DATA = VMAAS_DIR.joinpath("vmaas", "reposcan", "test_data", "database", "test_data.sql")
VMAAS_PG_OLD = VMAAS_DIR.joinpath("vmaas", "reposcan", "test_data", "database", "vmaas_db_postgresql_old.sql")


@pytest.fixture(scope="session")
def db_conn():
    """Fixture for db connection."""
    conn = _create_db_conn()
    reset_db(conn)
    yield conn


def _create_db_conn():
    """Create database connection"""
    user = os.getenv("POSTGRESQL_USER", "FILL")
    host = os.getenv("POSTGRESQL_HOST", "FILL")
    password = os.getenv("POSTGRESQL_PASSWORD", "FILL")
    database = os.getenv("POSTGRESQL_DATABASE", "FILL")
    port = os.getenv("POSTGRESQL_PORT", "FILL")

    conn = psycopg2.connect(user=user, host=host, password=password, database=database, port=port)
    init_db()
    return conn


def reset_db(conn, old_schema: bool = False):
    """Reset database schema, optionally use old schema to test upgrade."""

    with conn.cursor() as cursor:
        cursor.execute("DROP SCHEMA public CASCADE")
        cursor.execute("CREATE SCHEMA public")
        cursor.execute("GRANT ALL ON SCHEMA public TO public")

    with conn.cursor() as cursor:
        cursor.execute("DROP USER IF EXISTS vmaas_reader")
        cursor.execute("DROP USER IF EXISTS vmaas_writer")
        cursor.execute(USER_CREATE_SQL_PATH.read_text(encoding="utf-8"))
        if old_schema:
            cursor.execute(VMAAS_PG_OLD.read_text(encoding="utf-8"))
        else:
            cursor.execute(DB_CREATE_SQL_PATH.read_text(encoding="utf-8"))

    conn.commit()


def write_testing_data(conn):
    """Write testing data to the database."""
    with conn.cursor() as cursor:
        cursor.execute(VMAAS_DB_DATA.read_text(encoding="utf-8"))
    conn.commit()

@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client

@pytest.fixture
def client_class(request, client):
    if request.cls is not None:
        request.cls.client = client
