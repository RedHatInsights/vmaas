"""
Module containing class for syncing set of CSAF files into the DB.
"""
import json
import os
import shutil
import tempfile
from pathlib import Path

from vmaas.common.batch_list import BatchList
from vmaas.common.config import Config
from vmaas.common.logging_utils import get_logger
from vmaas.common.strtobool import strtobool
from vmaas.reposcan.database.csaf_store import CsafStore
from vmaas.reposcan.download.downloader import DownloadItem
from vmaas.reposcan.download.downloader import FileDownloader
from vmaas.reposcan.download.downloader import VALID_HTTP_CODES
from vmaas.reposcan.mnm import CSAF_FAILED_DOWNLOAD
from vmaas.reposcan.redhatcsaf.modeling import CsafCves
from vmaas.reposcan.redhatcsaf.modeling import CsafData
from vmaas.reposcan.redhatcsaf.modeling import CsafFile
from vmaas.reposcan.redhatcsaf.modeling import CsafFiles
from vmaas.reposcan.redhatcsaf.modeling import CsafProduct
from vmaas.reposcan.redhatcsaf.modeling import CsafProducts
from vmaas.reposcan.redhatcsaf.modeling import CsafProductStatus

CSAF_VEX_BASE_URL = os.getenv("CSAF_VEX_BASE_URL", "https://access.redhat.com/security/data/csaf/beta/vex/")
CSAF_VEX_INDEX_CSV = os.getenv("CSAF_VEX_INDEX_CSV", "changes.csv")
CSAF_SYNC_ALL_FILES = strtobool(os.getenv("CSAF_SYNC_ALL_FILES", "true"))


class CsafController:
    """Class for importing/syncing set of CSAF files into DB."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.downloader = FileDownloader()
        self.downloader.num_threads = 1  # rh.com returns 403 when downloading too quickly (DDoS protection?)
        self.csaf_store = CsafStore()
        self.tmp_directory = Path(tempfile.mkdtemp(prefix="csaf-"))
        self.index_path = self.tmp_directory / CSAF_VEX_INDEX_CSV
        self.cfg = Config()

    def _download_index(self) -> dict[str, int]:
        """Download CSAF index changes.csv file."""
        item = DownloadItem(source_url=CSAF_VEX_BASE_URL + CSAF_VEX_INDEX_CSV, target_path=self.index_path)
        self.downloader.add(item)
        self.downloader.run()
        # return failed download
        if item.status_code not in VALID_HTTP_CODES:
            return {item.target_path: item.status_code}
        return {}

    def _download_csaf_files(self, batch) -> dict[str, int]:
        """Download CSAF files."""
        download_items = []
        for csaf_file in batch:
            local_path = self.tmp_directory / csaf_file.name
            os.makedirs(os.path.dirname(local_path), exist_ok=True)  # Make sure subdirs exist
            item = DownloadItem(source_url=CSAF_VEX_BASE_URL + csaf_file.name, target_path=local_path)
            # Save for future status code check
            download_items.append(item)
            self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {
            item.target_path: item.status_code for item in download_items if item.status_code not in VALID_HTTP_CODES
        }

    def clean(self):
        """Clean downloaded files for given batch."""
        if self.tmp_directory:
            shutil.rmtree(self.tmp_directory)
            self.tmp_directory = None

    def store(self):
        """Process and store CSAF objects to DB."""
        self.logger.info("Checking CSAF index.")
        failed = self._download_index()
        if failed:
            CSAF_FAILED_DOWNLOAD.inc()
            target, status = failed.popitem()
            self.logger.warning("CSAF index failed to download, %s (HTTP CODE %d).", target, status)
            self.clean()
            return

        db_csaf_files = self.csaf_store.csaf_file_map.copy()
        batches = BatchList()
        csaf_files = CsafFiles.from_table_map_and_csv(db_csaf_files, self.index_path)
        files_to_sync = csaf_files
        if not CSAF_SYNC_ALL_FILES:
            files_to_sync = csaf_files.out_of_date

        for csaf_file in files_to_sync:
            batches.add_item(csaf_file)

        self.logger.info("%d CSAF files.", len(csaf_files))
        self.logger.info("%d CSAF files need to be synced.", len(list(files_to_sync)))

        try:
            for i, batch in enumerate(batches, 1):
                self.logger.info("Syncing a batch of %d CSAF files [%d/%d]", len(batch), i, len(batches))
                failed = self._download_csaf_files(batch)
                if failed:
                    CSAF_FAILED_DOWNLOAD.inc(len(failed))
                    self.logger.warning("%d CSAF files failed to download.", len(failed))
                    batch = [f for f in batch if (self.tmp_directory / f.name) not in failed]

                to_store = CsafData()
                for csaf_file in batch:
                    to_store.files[csaf_file.name] = csaf_file
                    to_store.cves.update(self.parse_csaf_file(csaf_file))

                self.csaf_store.store(to_store)
        finally:
            self.clean()

    def parse_csaf_file(self, csaf_file: CsafFile) -> CsafCves:
        """Parse CSAF file to CsafCves."""
        product_cpe = {}
        cves = CsafCves()

        with open(self.tmp_directory / csaf_file.name, "r", encoding="utf-8") as csaf_json:
            csaf = json.load(csaf_json)
            product_cpe = self._parse_product_tree(csaf)
            unfixed_cves = self._parse_vulnerabilities(csaf, product_cpe)
            cves.update(unfixed_cves)
        return cves

    def _parse_vulnerabilities(self, csaf: dict, product_cpe: dict) -> CsafCves:
        # parse only CVEs with `known_affected` products aka `unfixed` CVEs
        if any(x != "known_affected" for x in self.cfg.csaf_product_status_list):
            raise NotImplementedError("parsing of csaf products other than 'known_affected' not supported")

        unfixed_cves = CsafCves()
        for vulnerability in csaf["vulnerabilities"]:
            if "cve" not in vulnerability:
                # `vulnerability` can be identified by `cve` or `ids`, we are interested only in those with `cve`
                continue

            cve = vulnerability["cve"].upper()
            unfixed_cves[cve] = CsafProducts()
            for product_status in self.cfg.csaf_product_status_list:
                status_id = CsafProductStatus[product_status.upper()].value
                for unfixed in vulnerability["product_status"].get(product_status.lower(), []):
                    branch_product, rest = unfixed.split(":", 1)
                    pkg_name = rest
                    module = None
                    if "/" in rest:
                        # it's a package with a module
                        module, pkg_name = rest.split("/", 1)

                    csaf_product = CsafProduct(product_cpe[branch_product], pkg_name, status_id, module)
                    unfixed_cves[cve].append(csaf_product)

        return unfixed_cves

    def _parse_product_tree(self, csaf: dict) -> dict[str, str]:
        product_cpe: dict[str, str] = {}
        for branches in csaf.get("product_tree", {}).get("branches", []):
            self._parse_branches(branches, product_cpe)

        return product_cpe

    def _parse_branches(self, branches: dict, product_cpe: dict[str, str]):
        if branches.get("category") not in ("vendor", "product_family"):
            return
        sub_branches = branches.get("branches", [])
        for sub_branch in sub_branches:
            if "branches" in sub_branch:
                self._parse_branches(sub_branch, product_cpe)

            if sub_branch.get("category") != "product_name":
                continue

            product = sub_branch.get("product", {})
            product_id = product.get("product_id")
            cpe = product.get("product_identification_helper", {}).get("cpe")
            if product_id is None or cpe is None:
                continue
            product_cpe[product_id] = cpe
