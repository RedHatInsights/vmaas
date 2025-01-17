"""
Module containing class for syncing RHEL release metadata into database.
"""
from datetime import date

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.release_store import ReleaseStore
from vmaas.reposcan.redhatrelease.modeling import Release

OS_DB_NAME = "RHEL"


class ReleaseController:
    """Class for importing/syncing RHEL release metadata into DB."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.release_store = ReleaseStore()

    def _prepare_data(self, releases: dict[str, str]) -> list[Release]:
        release_list = []
        for release, ga_date in releases.items():
            major, minor = release.split(".", 1)
            release_list.append(
                Release(
                    OS_DB_NAME,
                    int(major),
                    int(minor),
                    date.fromisoformat(ga_date)
                )
            )
        return release_list

    def store(self, releases: dict[str, str]) -> None:
        """Process and store RHEL releases to DB."""
        self.logger.info("Syncing RHEL release metadata.")
        if not releases:
            raise ValueError("Empty release map")

        self.release_store.store(self._prepare_data(releases))
