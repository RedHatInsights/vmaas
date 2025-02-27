"""
Module containing class for syncing RHEL release metadata into database.
"""
from datetime import date
import json
import os
import subprocess
import tempfile

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.release_store import ReleaseStore
from vmaas.reposcan.redhatrelease.modeling import LifecyclePhase
from vmaas.reposcan.redhatrelease.modeling import Release

ALLOWED_LONG_TERM_RELEASES = os.getenv("ALLOWED_LONG_TERM_RELEASES", "eus,aus").split(",")

GEN_PACKAGES_SCRIPT = "/usr/local/bin/gen_package_profile.py"
OS_DB_NAME = "RHEL"


class ReleaseController:
    """Class for importing/syncing RHEL release metadata into DB."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.release_store = ReleaseStore()

    def _get_dnf_package_list(self, release: Release, repositories: dict[str, dict[LifecyclePhase, list[tuple[str, str, str, str, str]]]]) -> list[str]:
        with tempfile.TemporaryDirectory(prefix=f"dnf-{release.major}.{release.minor}-") as tmpdirname:
            dnf_env = {"DNF_CACHEDIR": tmpdirname,
                       "DNF_REPOS": json.dumps(repositories[f"{release.major}.{release.minor}"][LifecyclePhase.MINOR]),
                       "DNF_PLATFORM_ID": f"platform:el{release.major}"}
            proc = subprocess.run([GEN_PACKAGES_SCRIPT], env=dnf_env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if proc.returncode != 0:
            self.logger.error("Executing package generation script failed: %s", proc.stderr)
            raise ValueError("Unable to get valid package list")

        # Extract package list from external script output
        package_list: list[str] = json.loads(proc.stdout)["package_list"]
        return package_list

    def _generate_system_profile(self, release: Release, latest_releases: dict[int, int],
                                 repositories: dict[str, dict[LifecyclePhase, list[tuple[str, str, str, str, str]]]]) -> None:
        self.logger.info("Generating system profile for release %d.%d (%s).", release.major, release.minor, release.lifecycle_phase)
        release.system_profile["package_list"] = sorted(self._get_dnf_package_list(release, repositories))
        release.system_profile["repository_list"] = sorted([label for (label, _, _, _, _)
                                                            in repositories[f"{release.major}.{release.minor}"][release.lifecycle_phase]])
        release.system_profile["basearch"] = "x86_64"
        # Minor release: show updates from minor release to latest minor release
        # EUS (and similar) release: show updates from minor release to EUS of the same minor release
        if release.lifecycle_phase == LifecyclePhase.MINOR:
            release.system_profile["releasever"] = f"{release.major}.{latest_releases[release.major]}"
        else:
            release.system_profile["releasever"] = f"{release.major}.{release.minor}"

    def _prepare_data(self, releases: dict[str, str]) -> list[Release]:
        repositories = self.release_store.get_repositories(list(releases), ALLOWED_LONG_TERM_RELEASES)
        latest_releases: dict[int, int] = {}
        release_list = []
        for release_s, ga_date_s in releases.items():
            ga_date = date.fromisoformat(ga_date_s)
            # Filter out release versions not out yet, or those without repositories
            if date.today() < ga_date or release_s not in repositories:
                continue
            major_s, minor_s = release_s.split(".", 1)
            major, minor = int(major_s), int(minor_s)
            if major not in latest_releases or minor > latest_releases[major]:
                latest_releases[major] = minor
            for lifecycle_phase in repositories[release_s]:
                release_list.append(
                    Release(
                        OS_DB_NAME,
                        major,
                        minor,
                        lifecycle_phase,
                        ga_date,
                        {}
                    )
                )
        for release in release_list:
            self._generate_system_profile(release, latest_releases, repositories)
        return release_list

    def store(self, releases: dict[str, str]) -> None:
        """Process and store RHEL releases to DB."""
        self.logger.info("Syncing RHEL release metadata.")
        if not releases:
            raise ValueError("Empty release map")

        self.release_store.store(self._prepare_data(releases))
