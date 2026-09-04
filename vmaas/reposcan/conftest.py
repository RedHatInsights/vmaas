"""Pytest configuration for database tests."""

import os

from pathlib import Path
import psycopg2
import pytest

from vmaas.common.paths import DB_CREATE_SQL_PATH
from vmaas.reposcan.database.database_handler import init_db
from vmaas.reposcan.redhatcsaf import modeling as csaf_model

VMAAS_DIR = Path(__file__).resolve().parent.parent.parent
VMAAS_DB_DATA = VMAAS_DIR.joinpath("vmaas", "reposcan", "test_data", "database", "test_data.sql")
VMAAS_PG_OLD = VMAAS_DIR.joinpath("vmaas", "reposcan", "test_data", "database", "vmaas_db_postgresql_old.sql")

EXPECTED_CSAF = (
    ("cve-2023-0030.json", csaf_model.CsafCves({"CVE-2023-0030": csaf_model.CsafProducts()})),
    (
        "cve-2023-0049.json",
        csaf_model.CsafCves(
            {
                "CVE-2023-0049": csaf_model.CsafProducts([
                    csaf_model.CsafProduct("cpe:/o:redhat:enterprise_linux:6", "vim", 4),
                    csaf_model.CsafProduct("cpe:/o:redhat:enterprise_linux:7", "vim", 4),
                    csaf_model.CsafProduct("cpe:/o:redhat:enterprise_linux:8", "vim", 4),
                    csaf_model.CsafProduct("cpe:/o:redhat:enterprise_linux:9", "vim", 4),
                ])
            }
        ),
    ),
    (
        "cve-2023-1017.json",
        csaf_model.CsafCves(
            {
                "CVE-2023-1017": csaf_model.CsafProducts([
                    csaf_model.CsafProduct("cpe:/o:redhat:enterprise_linux:8", "libtpms", 4, "virt:rhel"),
                    csaf_model.CsafProduct("cpe:/a:redhat:advanced_virtualization:8::el8", "libtpms", 4, "virt:8.2"),
                    csaf_model.CsafProduct("cpe:/a:redhat:advanced_virtualization:8::el8", "libtpms", 4, "virt:8.3"),
                    csaf_model.CsafProduct("cpe:/a:redhat:advanced_virtualization:8::el8", "libtpms", 4, "virt:av"),
                    csaf_model.CsafProduct(
                        "cpe:/a:redhat:rhel_eus:8.6::appstream",
                        "SLOF-0:20210217-1.module+el8.6.0+14480+c0a3aa0f.noarch",
                        3,
                        None,
                        "RHSA-2023:1833",
                        variant_suffix="8.6.0.Z.EUS",
                    ),
                    csaf_model.CsafProduct(
                        "cpe:/a:redhat:rhel_eus:8.6::appstream",
                        "SLOF-0:20210217-1.module+el8.6.0+14480+c0a3aa0f.src",
                        3,
                        "virt:rhel",
                        "RHSA-2023:1833",
                        variant_suffix="8.6.0.Z.EUS",
                    ),
                ])
            }
        ),
    ),
)


@pytest.fixture(autouse=True)
def _stop_leftover_sync_task():
    """Ensure no background sync worker survives a test and pollutes the shared DB.

    Reposcan API tests (e.g. test_add_repo_*) POST to /api/v1/repos, which starts an
    asynchronous import in a separate spawned SyncTask worker process with its own DB
    connection. That import is only best-effort cancelled by the test. If the worker is
    still running when a later test runs, it can commit rows (such as the
    'testing-repo-name' content_set) to the shared test database after that test's
    reset_db(), causing intermittent failures like test_integration.test_phase_1
    (assert 2 == 1). Terminate any worker still running at teardown so it cannot leak a
    late commit across a test boundary; any row it already committed is then removed by
    the next test's reset_db().
    """
    yield
    # Imported lazily so collection never depends on the sync worker being initialized.
    from vmaas.reposcan.reposcan import SyncTask  # pylint: disable=import-outside-toplevel

    if SyncTask.workers is not None and SyncTask.is_running():
        SyncTask.cancel()


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
        if old_schema:
            cursor.execute(VMAAS_PG_OLD.read_text(encoding="utf-8"))
        else:
            cursor.execute(DB_CREATE_SQL_PATH.read_text(encoding="utf-8"))

    conn.commit()


def write_testing_data(conn: psycopg2.extensions.connection) -> None:
    """Write testing data to the database."""
    with conn.cursor() as cursor:
        cursor.execute(VMAAS_DB_DATA.read_text(encoding="utf-8"))
    conn.commit()


@pytest.fixture
def client(app):
    """Get client."""
    with app.test_client() as client:  # pylint: disable=redefined-outer-name
        yield client


@pytest.fixture
def client_class(request, client):   # pylint: disable=redefined-outer-name
    """Get client class."""
    if request.cls is not None:
        request.cls.client = client
