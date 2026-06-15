#!/usr/bin/env python3
"""
Cleanup repository rows whose URL still contains $releasever or $basearch placeholders
and were never synced (revision IS NULL, just as a safety check but repos should match)
"""
import argparse
import sys

from vmaas.common.logging_utils import get_logger, init_logging
from vmaas.reposcan.database.database_handler import DatabaseHandler, init_db
from vmaas.reposcan.database.repository_store import RepositoryStore

LOGGER = get_logger(__name__)

UNRESOLVED_PLACEHOLDER_REPOS_SQL = """select cs.label, a.name, r.releasever, o.name, r.url
                                      from repo r
                                      join content_set cs on cs.id = r.content_set_id
                                      join organization o on o.id = r.org_id
                                      left join arch a on a.id = r.basearch_id
                                      where (r.url like %s or r.url like %s)
                                      and r.revision is null""" # is null just safety condition 


def find_placeholder_repos(conn):
    with conn.cursor() as cur:
        cur.execute(UNRESOLVED_PLACEHOLDER_REPOS_SQL, ('%$releasever%', '%$basearch%'))
        return cur.fetchall()


def main():
    parser = argparse.ArgumentParser(
        description="Delete never-synced repos whose URL still contains $releasever or $basearch"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List repositories that would be deleted without modifying the database",
    )
    args = parser.parse_args()

    init_logging()
    init_db()
    conn = DatabaseHandler.get_connection()
    try:
        repos = find_placeholder_repos(conn)
        if not repos:
            LOGGER.info("No unresolved placeholder repositories found. No changes were made.")
            return 0

        for content_set, basearch, releasever, organization, url in repos:
            LOGGER.info(
                "Unresolved placeholder repository: %s (%s)",
                ", ".join(filter(None, (content_set, basearch, releasever, organization))),
                url,
            )

        if args.dry_run:
            LOGGER.info("Dry run: %d repositories will be deleted", len(repos))
            return 0

        repo_store = RepositoryStore()
        for content_set, basearch, releasever, organization, _url in repos:
            # Delete using content_set likely to be safe, vmaas_db_postgresql.sql Lines 477-480
            repo_store.delete_content_set(
                content_set, basearch=basearch, releasever=releasever, organization=organization,
            )
        # cleans orphaned packages and errata left behind after repo deletion
        repo_store.cleanup_unused_data()
        LOGGER.info("Removed %d unresolved placeholder repositories", len(repos))
    except Exception:  # pylint: disable=broad-except
        LOGGER.exception("Placeholder repository cleanup failed")
        DatabaseHandler.rollback()
        return 1
    finally:
        DatabaseHandler.close_connection()

    return 0


if __name__ == "__main__":
    sys.exit(main())
