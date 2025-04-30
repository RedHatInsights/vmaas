"""
Module containing code interacting with Satellite/Katello server.
"""
import os
import shutil
import tempfile

import requests

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.repository_store import RepositoryStore

LOGGER = get_logger(__name__)

KATELLO_CA_CERT_PATH = "/pub/katello-server-ca.crt"
KATELLO_ACCESS_CERT_PATH = "/katello/api/v2/organizations/%s/download_debug_certificate"
KATELLO_ORG_LIST_API = "/katello/api/v2/organizations"
KATELLO_REPOS_LIST_API = "/katello/api/v2/repositories?organization_id=%s&search=redhat=true"

RETRY_COUNT = int(os.getenv("RETRY_COUNT", "3"))


class KatelloApi:
    """Class used to obtain information from Satellite/Katello API."""
    def __init__(self, hostname: str, api_user: str, api_pass: str):
        self.hostname: str = hostname
        self.api_user: str = api_user
        self.api_pass: str = api_pass

        self.tmp_directory: str | None = None

        repo_store: RepositoryStore = RepositoryStore()
        self.archs: list[str] = repo_store.list_archs()

        self.success: bool = False

    def _rm_tmpdir(self) -> None:
        if self.tmp_directory:
            LOGGER.debug("Deleting tmp dir: %s", self.tmp_directory)
            shutil.rmtree(self.tmp_directory)
        self.tmp_directory = None

    def _find_arch(self, url: str) -> str | None:
        for arch in self.archs:
            if arch in url:
                return arch
        return None

    def _fetch_katello(  # pylint: disable=too-many-branches
        self, endpoint, scheme="https", json=True, timeout=30, **kwargs
    ) -> dict:
        """Sends request to Katello server/API"""

        if scheme == "https":
            verify = os.path.join(self.tmp_directory, os.path.basename(KATELLO_CA_CERT_PATH))
            if not os.path.isfile(verify):
                LOGGER.error("Katello CA certificate not found! Skipping API call.")
                self.success = False
                return {}
            auth = (self.api_user, self.api_pass)
        else:
            verify = True
            auth = None

        if json:
            headers = {"Accept": "application/json"}
        else:
            headers = {}

        url = f"{scheme}://{self.hostname}{endpoint}"
        tries = 0

        while True:
            if tries >= RETRY_COUNT:
                break
            try:
                response = requests.request(
                    method="GET",
                    url=url,
                    headers=headers,
                    timeout=timeout,
                    auth=auth,
                    verify=verify,
                    **kwargs,
                )
                if response.status_code == 200:
                    if json:
                        return response.json()
                    return {"data": response.text}

                tries += 1
                LOGGER.error("Error during GET request to url %s: HTTP %s, %s", url, response.status_code, response.text)
                # Do not retry for 4xx HTTP codes
                if 400 <= response.status_code < 500:
                    break
            except requests.exceptions.RequestException:
                tries += 1
                LOGGER.exception("Error calling API %s: ", url)
        self.success = False
        return {}

    def _download_katello_ca_certificate(self) -> str | None:
        LOGGER.info("Downloading Katello CA certificate.")

        ca_certificate = self._fetch_katello(KATELLO_CA_CERT_PATH, scheme="http", json=False)
        if not ca_certificate:
            LOGGER.error("Katello CA certificate download failed.")
            self.success = False
            return None

        # Write CA certificate to tempfile to be able to use with requests
        with open(os.path.join(self.tmp_directory, os.path.basename(KATELLO_CA_CERT_PATH)), "w", encoding="utf-8") as ca_cert_tmpfile:
            ca_cert_tmpfile.write(ca_certificate["data"])

        return ca_certificate["data"]

    def _download_katello_access_certificate(self, org_id: int, org_label: str) -> str | None:
        LOGGER.info("Downloading Katello organization '%s' access certificate.", org_label)

        access_certificate_key = self._fetch_katello(KATELLO_ACCESS_CERT_PATH % org_id, json=False)
        if not access_certificate_key:
            LOGGER.error("Katello access certificate download failed, skipping organization '%s'.", org_label)
            self.success = False
            return None

        return access_certificate_key["data"]

    def _get_orgs(self) -> dict[int, str]:
        org_results = self._fetch_katello(KATELLO_ORG_LIST_API)
        return {result["id"]: result["label"] for result in org_results.get("results", [])}

    def _get_org_repos(self, org_id: int, org_label: str, ca_cert: str, products: dict) -> list[tuple]:
        LOGGER.info("Getting organization '%s' repositories.", org_label)

        repos = []

        access_cert = self._download_katello_access_certificate(org_id, org_label)
        if not access_cert:
            return repos

        repo_results = self._fetch_katello(KATELLO_REPOS_LIST_API % org_id)

        for repo in repo_results.get("results", []):
            content_label = repo["content_label"]
            if repo["content_type"] != "yum":
                LOGGER.debug("Skipping repo '%s' - not a yum repo.", content_label)
                continue
            product_name = repo["product"]["name"]
            cs_label = repo["content_label"]
            cs_name = repo["name"]
            url = repo["full_path"]
            releasever = repo["minor"]

            basearch = self._find_arch(url)
            if not basearch:
                LOGGER.warning("Skipping repo '%s' - unknown basearch.", content_label)
                continue

            # Update product dict with unique product names and content sets
            if product_name not in products:
                products[product_name] = {"product_id": None, "content_sets": {}}
            if cs_label not in products[product_name]["content_sets"]:
                products[product_name]["content_sets"][cs_label] = {"name": cs_name}

            repos.append((url, cs_label, basearch, releasever, org_label, ca_cert, access_cert, None, org_label))

        return repos

    def get_products_repos(self) -> tuple[dict, list, bool]:
        """Generate product map and repository list from Katello API."""
        self.success = True
        products, repos = {}, []
        try:
            self.tmp_directory = tempfile.mkdtemp(prefix="katello-")
            ca_cert = self._download_katello_ca_certificate()
            orgs = self._get_orgs()
            for org_id, org_label in orgs.items():
                repos.extend(self._get_org_repos(org_id, org_label, ca_cert, products))
        finally:
            self._rm_tmpdir()
        return products, repos, self.success
