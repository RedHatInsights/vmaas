"""
Module containing class for fetching/importing RHEL release metadata from/into database.
"""
from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.database_handler import DatabaseHandler
from vmaas.reposcan.mnm import RELEASE_FAILED_IMPORT
from vmaas.reposcan.redhatrelease.modeling import Release


class ReleaseStore:
    """
    Class providing interface for storing release version metadata.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()

    def _sync_releases(self, releases: list[Release]) -> None:
        self.logger.info("Syncing %d operating system releases.", len(releases))
        cur = self.conn.cursor()
        exists_in_db = {}
        try:
            cur.execute("SELECT name, major, minor, ga FROM operating_system")
            for name, major, minor, ga_date in cur.fetchall():
                exists_in_db[(name, major, minor)] = ga_date

            to_insert, to_update, to_delete = [], [], []
            for release in releases:
                if (release.os_name, release.major, release.minor) not in exists_in_db:
                    to_insert.append(release)
                else:
                    if release.ga_date != exists_in_db[(release.os_name, release.major, release.minor)]:
                        to_update.append(release)
                    del exists_in_db[(release.os_name, release.major, release.minor)]
            to_delete.extend([Release(name, major, minor, ga_date) for (name, major, minor), ga_date in exists_in_db.items()])

            self.logger.debug("Releases to insert: %d", len(to_insert))
            self.logger.debug("Releases to update: %d", len(to_update))
            self.logger.debug("Releases to delete: %d", len(to_delete))

            for release in to_insert:
                cur.execute("INSERT INTO operating_system (name, major, minor, ga) VALUES (%s, %s, %s, %s)",
                            (release.os_name, release.major, release.minor, release.ga_date))

            for release in to_update:
                cur.execute("UPDATE operating_system SET ga = %s WHERE name = %s AND major = %s AND minor = %s",
                            (release.ga_date, release.os_name, release.major, release.minor))

            for release in to_delete:
                cur.execute("DELETE FROM operating_system WHERE name = %s AND major = %s AND minor = %s",
                            (release.os_name, release.major, release.minor))

            self.conn.commit()
        except Exception:  # pylint: disable=broad-except
            self.logger.exception("Failed to insert/update/delete into/from operating_system.")
            self.conn.rollback()
            RELEASE_FAILED_IMPORT.inc()
        finally:
            cur.close()

    def store(self, releases: list[Release]) -> None:
        """
        Sync all release versions from input list with DB.
        """
        self._sync_releases(releases)
