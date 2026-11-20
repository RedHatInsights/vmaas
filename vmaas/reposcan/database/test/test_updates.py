"""Unit tests of update_store.py."""
import typing as t
from datetime import datetime

import pytest
from psycopg2.extensions import connection
from psycopg2.extras import execute_values

from vmaas.reposcan.conftest import reset_db
from vmaas.reposcan.conftest import write_testing_data
from vmaas.reposcan.database.update_store import UpdateStore

REPO_ID = 801
ERRATA_ID = 401
# Module stream of module1 in repo 801 (see test_data.sql). The bulk
# associations carry it so they match the row-tuple comparison and are
# queued for disassociation ("module_id in module_ids_in_repo" guard).
BULK_MODULE_STREAM_ID = 1103
# Number of orphaned pkg_errata associations to disassociate. Row-comparison
# IN lists overflow Postgres max_stack_depth (2MB default, 6144kB tuned) well
# below this count when the DELETE is not batched.
BULK_ASSOCIATIONS = 50000

UPDATE_ERRATA1 = {
    "from": "updates@repourl.com",
    "status": "final",
    "version": "1",
    "type": "security",
    "id": "errata1",
    "title": "errata1 title",
    "reboot": False,
    "summary": "summary1",
    "rights": None,
    "description": "description1",
    "release": None,
    "solution": "solution1",
    "severity": "Important",
    "issued": datetime(2019, 1, 1, 1, 0, 0),
    "updated": datetime(2019, 1, 1, 2, 0, 22),
    "references": [],
    "pkglist": [
        # NEVRA + module of package 301, associated with errata 401 in repo 801
        {
            "name": "pkg-sec-errata1",
            "epoch": "1",
            "ver": "1",
            "rel": "1",
            "arch": "noarch",
            "module_name": "module1",
            "module_stream": "stream1",
            "module_version": 11,
            "module_context": "fun1",
            "module_arch": "noarch",
        }
    ],
}


# pylint: disable=protected-access
class TestUpdateStore:
    """UpdateStore tests."""

    @pytest.fixture
    def update_store(self, db_conn: connection) -> t.Generator[UpdateStore, None, None]:  # pylint: disable=unused-argument
        """Fixture returning UpdateStore obj and cleaning db after test.

        The schema is also reset on setup: earlier test modules commit rows
        (e.g. errata_refs, cve_cwe) into the session-shared database that
        write_testing_data() does not clean up. The session connection is
        rolled back first to release locks of its open transaction, otherwise
        the DROP SCHEMA below would block on it.
        """
        db_conn.rollback()
        store = UpdateStore()
        reset_db(store.conn)
        yield store
        reset_db(store.conn)

    def _setup_bulk_associations(self, store: UpdateStore, count: int) -> None:
        """Associate a large number of extra packages with errata1 in repo 801."""
        write_testing_data(store.conn)
        package_names = tuple((10_000 + i, f"pkg-bulk-{i}") for i in range(count))
        packages = tuple((10_000 + i, 10_000 + i, 201, 1, None, None) for i in range(count))
        pkg_repo = tuple((10_000 + i, REPO_ID) for i in range(count))
        pkg_errata = tuple((10_000 + i, ERRATA_ID, BULK_MODULE_STREAM_ID) for i in range(count))

        with store.conn.cursor() as cur:
            execute_values(cur, "INSERT INTO package_name(id, name) VALUES %s", package_names)
            execute_values(
                cur, "INSERT INTO package(id, name_id, evr_id, arch_id, summary, description) VALUES %s", packages
            )
            execute_values(cur, "INSERT INTO pkg_repo(pkg_id, repo_id) VALUES %s", pkg_repo)
            execute_values(cur, "INSERT INTO pkg_errata(pkg_id, errata_id, module_stream_id) VALUES %s", pkg_errata)
        store.conn.commit()

    def _errata_pkg_count(self, store: UpdateStore) -> int:
        """Count pkg_errata rows of errata1 associated with repo 801."""
        with store.conn.cursor() as cur:
            cur.execute(
                """select count(*) from pkg_errata pe join pkg_repo pr
                   on pr.pkg_id = pe.pkg_id and pr.repo_id = %s
                   where pe.errata_id = %s""",
                (REPO_ID, ERRATA_ID),
            )
            return cur.fetchone()[0]

    def test_associate_packages_bulk_disassociate(self, update_store: UpdateStore) -> None:
        """Test that _associate_packages handles a large number of disassociations.

        A repo sync removing many pkg_errata associations used to raise
        StatementTooComplex (stack depth limit exceeded) on the bulk DELETE.
        """
        self._setup_bulk_associations(update_store, BULK_ASSOCIATIONS)
        # packages 301 and 302 from test data plus the bulk associations
        assert self._errata_pkg_count(update_store) == BULK_ASSOCIATIONS + 2

        update_store.store(REPO_ID, [UPDATE_ERRATA1])

        # All orphaned bulk associations are gone.
        with update_store.conn.cursor() as cur:
            cur.execute("select count(*) from pkg_errata where pkg_id >= 10000")
            assert cur.fetchone()[0] == 0

        # (302, 401, 1103) is no longer referenced by the repo metadata and is
        # removed; _associate_source_packages keeps the source package of the
        # still associated binary package 307 (repo 802) and drops (301, 401, 1101).
        with update_store.conn.cursor() as cur:
            cur.execute(
                "select pkg_id, module_stream_id from pkg_errata where errata_id = %s order by pkg_id",
                (ERRATA_ID,),
            )
            assert cur.fetchall() == [(302, 1102), (307, 1102)]
