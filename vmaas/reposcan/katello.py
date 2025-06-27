"""
Module containing code interacting with Satellite/Katello server.
"""
import os
import shutil
import tempfile
from urllib.parse import urlparse

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util import Retry

from vmaas.common.logging_utils import get_logger
from vmaas.reposcan.database.repository_store import RepositoryStore

LOGGER = get_logger(__name__)

KATELLO_URL = os.getenv("KATELLO_URL", "")  # https://satellite.example.com
KATELLO_API_USER = os.getenv("KATELLO_API_USER", "admin")
KATELLO_API_PASS = os.getenv("KATELLO_API_PASS", "changeme")

KATELLO_CA_CERT_PATH = "/katello-server-ca.crt"

KATELLO_ACCESS_CERT_API = "/katello/api/v2/organizations/%s/download_debug_certificate"
KATELLO_ORG_LIST_API = "/katello/api/v2/organizations"
KATELLO_REPOS_LIST_API = "/katello/api/v2/repositories?organization_id=%s&search=redhat=true"

RETRY_COUNT = int(os.getenv("RETRY_COUNT", "3"))


class KatelloApiException(Exception):
    """Error happened during Katello API usage."""


class KatelloApi:
    """Class used to obtain information from Satellite/Katello API."""
    def __init__(self, url: str, api_user: str, api_pass: str):
        self.url: str = url
        self.api_user: str = api_user
        self.api_pass: str = api_pass

        self.session = Session()
        retries = Retry(
            total=RETRY_COUNT,
            backoff_factor=2,
        )
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        self.tmp_directory: str | None = None

        repo_store: RepositoryStore = RepositoryStore()
        self.archs: list[str] = repo_store.list_archs()

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

    def _fetch_katello(
        self, endpoint, json=True, timeout=30, **kwargs
    ) -> dict:
        """Sends request to Katello server/API"""
        url = f"{self.url}{endpoint}"
        parsed_url = urlparse(url)

        if parsed_url.scheme == "https":
            kwargs["verify"] = KATELLO_CA_CERT_PATH
            if not os.path.isfile(KATELLO_CA_CERT_PATH):
                msg = f"Katello CA certificate is missing in path '{KATELLO_CA_CERT_PATH}'."
                raise KatelloApiException(msg)


        if json:
            headers = {"Accept": "application/json"}
        else:
            headers = {}

        try:
            response = self.session.request(
                method="GET",
                url=url,
                headers=headers,
                timeout=timeout,
                auth=(self.api_user, self.api_pass),
                **kwargs,
            )
            if response.status_code == 200:
                if json:
                    return response.json()
                return {"data": response.text}

            LOGGER.error("Error during GET request to url %s: HTTP %s, %s", url, response.status_code, response.text)
        except RequestException:
            LOGGER.exception("Error calling API %s: ", url)

        return {}

    def _load_katello_ca_certificate(self) -> str:
        if not os.path.isfile(KATELLO_CA_CERT_PATH):
            msg = f"Katello CA certificate is missing in path '{KATELLO_CA_CERT_PATH}'."
            raise KatelloApiException(msg)

        with open(KATELLO_CA_CERT_PATH, encoding="utf-8") as cert_file:
            cert = cert_file.read()

        return cert

    def _download_katello_access_certificate(self, org_id: int, org_label: str) -> str:
        LOGGER.info("Downloading Katello organization '%s' access certificate.", org_label)

        access_certificate_key = self._fetch_katello(KATELLO_ACCESS_CERT_API % org_id, json=False)
        if not access_certificate_key:
            msg = f"Katello access certificate download failed, skipping organization '{org_label}'."
            raise KatelloApiException(msg)

        return access_certificate_key["data"]

    def _get_orgs(self) -> dict[int, str]:
        org_results = self._fetch_katello(KATELLO_ORG_LIST_API)
        if not org_results:
            msg = "Organizations API fetch failed."
            raise KatelloApiException(msg)

        return {result["id"]: result["label"] for result in org_results["results"]}

    def _get_org_repos(self, org_id: int, org_label: str, ca_cert: str, products: dict) -> list[tuple]:
        LOGGER.info("Getting organization '%s' repositories.", org_label)

        repos = []
        access_cert = self._download_katello_access_certificate(org_id, org_label)
        repo_results = self._fetch_katello(KATELLO_REPOS_LIST_API % org_id)
        if not repo_results:
            msg = "Repositories API fetch failed."
            raise KatelloApiException(msg)

        for repo in repo_results["results"]:
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
        products, repos = {}, []
        try:
            self.tmp_directory = tempfile.mkdtemp(prefix="katello-")
            ca_cert = self._load_katello_ca_certificate()
            orgs = self._get_orgs()
            for org_id, org_label in orgs.items():
                repos.extend(self._get_org_repos(org_id, org_label, ca_cert, products))
        except KatelloApiException as exc:
            LOGGER.error(exc)
            return products, repos, False
        finally:
            self._rm_tmpdir()
        return products, repos, True
