"""
Module containing class for fetching/importing RHEL release metadata from/into database.
"""
from psycopg2.extras import Json

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.database_handler import DatabaseHandler
from vmaas.reposcan.mnm import RELEASE_FAILED_IMPORT
from vmaas.reposcan.redhatrelease.modeling import LifecyclePhase
from vmaas.reposcan.redhatrelease.modeling import Release


class ReleaseStore:
    """
    Class providing interface for storing release version metadata.
    """

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.conn = DatabaseHandler.get_connection()

    @staticmethod
    def _get_lifecycle_phase(repo_label: str, allowed_long_term_releases: list[str]) -> LifecyclePhase:
        for long_term_release in allowed_long_term_releases:
            if f"-{long_term_release}-" in repo_label:
                return LifecyclePhase(long_term_release)
        return LifecyclePhase("minor")

    def get_repositories(self,
                         releases: list[str],
                         allowed_long_term_releases: list[str]) -> dict[str, dict[LifecyclePhase, list[tuple[str, str, str, str, str]]]]:
        """
        Get list of repository URLs for each releasever.
        (If the repository URL is available)
        """
        repositories: dict[str, dict[LifecyclePhase, list[tuple[str, str, str, str, str]]]] = {}
        cur = self.conn.cursor()
        cur.execute("""SELECT r.releasever, cs.label, r.url, c.ca_cert, c.cert, c.key
                       FROM content_set cs JOIN
                            repo r ON cs.id = r.content_set_id JOIN
                            arch a ON r.basearch_id = a.id LEFT JOIN
                            certificate c ON r.certificate_id = c.id
                       WHERE (cs.label SIMILAR TO %s OR
                              cs.label SIMILAR TO %s) AND
                             a.name = 'x86_64' AND
                             r.releasever = ANY(%s) AND
                             r.revision IS NOT NULL
                       ORDER BY r.releasever, cs.label, r.url""", (
                           f"rhel-_{{1,2}}-for-x86_64-(baseos|appstream)-(({"|".join(allowed_long_term_releases)})-)?rpms",
                           f"rhel-_-server-(({"|".join(allowed_long_term_releases)})-)?rpms",
                           releases
                       )
                    )
        for releasever, label, url, ca_cert, cert, key in cur.fetchall():
            lifecycle_phase = self._get_lifecycle_phase(label, allowed_long_term_releases)
            repositories.setdefault(releasever, {}).setdefault(lifecycle_phase, []).append((label, url, ca_cert, cert, key))
        cur.close()
        return repositories

    def _sync_releases(self, releases: list[Release]) -> None:
        cur = self.conn.cursor()
        exists_in_db = {}
        try:
            cur.execute("SELECT name, major, minor, lifecycle_phase, ga, system_profile FROM operating_system")
            for name, major, minor, lifecycle_phase, ga_date, system_profile in cur.fetchall():
                exists_in_db[(name, major, minor, lifecycle_phase)] = (ga_date, system_profile)

            to_insert, to_update, to_delete = [], [], []
            for release in releases:
                if (release.os_name, release.major, release.minor, release.lifecycle_phase) not in exists_in_db:
                    to_insert.append(release)
                else:
                    ga_date, system_profile = exists_in_db[(release.os_name, release.major, release.minor, release.lifecycle_phase)]
                    if release.ga_date != ga_date or release.system_profile != system_profile:
                        to_update.append(release)
                    del exists_in_db[(release.os_name, release.major, release.minor, release.lifecycle_phase)]
            to_delete.extend([Release(name, major, minor, lifecycle_phase, ga_date, system_profile)
                              for (name, major, minor, lifecycle_phase), (ga_date, system_profile) in exists_in_db.items()])

            self.logger.info("Syncing %d operating system releases. (i=%d, u=%d, d=%d)", len(releases), len(to_insert), len(to_update), len(to_delete))

            for release in to_insert:
                cur.execute("INSERT INTO operating_system (name, major, minor, lifecycle_phase, ga, system_profile) VALUES (%s, %s, %s, %s, %s, %s)",
                            (release.os_name, release.major, release.minor, release.lifecycle_phase, release.ga_date, Json(release.system_profile)))

            for release in to_update:
                cur.execute("UPDATE operating_system SET ga = %s, system_profile = %s WHERE name = %s AND major = %s AND minor = %s AND lifecycle_phase = %s",
                            (release.ga_date, Json(release.system_profile), release.os_name, release.major, release.minor, release.lifecycle_phase))

            for release in to_delete:
                cur.execute("DELETE FROM operating_system WHERE name = %s AND major = %s AND minor = %s AND lifecycle_phase = %s",
                            (release.os_name, release.major, release.minor, release.lifecycle_phase))

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
