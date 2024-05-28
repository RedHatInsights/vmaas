"""
Module containing class for syncing set of CSAF files into the DB.
"""
import json
import os
import re
import shutil
import tempfile
import typing as t
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
ERRATUM_RE = re.compile(r"RH[BSE]{1}A-2\d{3}:\d+")


class ComponentError(Exception):
    """CSAF component error."""


class CsafController:
    """Class for importing/syncing set of CSAF files into DB."""

    def __init__(self) -> None:
        self.logger = get_logger(__name__)
        self.downloader = FileDownloader()
        self.downloader.num_threads = 1  # rh.com returns 403 when downloading too quickly (DDoS protection?)
        self.csaf_store = CsafStore()
        self.tmp_directory: Path | None = Path(tempfile.mkdtemp(prefix="csaf-"))
        self.index_path = self.tmp_directory / CSAF_VEX_INDEX_CSV
        self.cfg = Config()

    def _download_index(self) -> dict[Path, int]:
        """Download CSAF index changes.csv file."""
        item = DownloadItem(source_url=CSAF_VEX_BASE_URL + CSAF_VEX_INDEX_CSV, target_path=self.index_path)
        self.downloader.add(item)
        self.downloader.run()
        # return failed download
        if item.status_code not in VALID_HTTP_CODES and item.target_path:
            return {item.target_path: item.status_code}
        return {}

    def _download_csaf_files(self, batch: list[CsafFile]) -> dict[Path, int]:
        """Download CSAF files."""
        download_items = []
        for csaf_file in batch:
            if not self.tmp_directory:
                self.logger.error("Missing temporary directory for csaf download")
                return {}
            local_path = self.tmp_directory / csaf_file.name
            os.makedirs(os.path.dirname(local_path), exist_ok=True)  # Make sure subdirs exist
            item = DownloadItem(source_url=CSAF_VEX_BASE_URL + csaf_file.name, target_path=local_path)
            # Save for future status code check
            download_items.append(item)
            self.downloader.add(item)
        self.downloader.run()
        # Return failed downloads
        return {
            item.target_path: item.status_code
            for item in download_items
            if item.status_code not in VALID_HTTP_CODES and item.target_path
        }

    def clean(self) -> None:
        """Clean downloaded files for given batch."""
        if self.tmp_directory:
            shutil.rmtree(self.tmp_directory)
            self.tmp_directory = None

    def store(self) -> None:
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
        csaf_files = CsafFiles.from_table_map_and_csv(db_csaf_files, self.index_path)  # type: ignore[arg-type]
        files_to_sync: t.Iterable[CsafFile] = csaf_files
        if not CSAF_SYNC_ALL_FILES:
            files_to_sync = csaf_files.out_of_date

        for csaf_file in files_to_sync:
            batches.add_item(csaf_file)

        self.logger.info("%d CSAF files.", len(csaf_files))
        self.logger.info("%d CSAF files need to be synced.", batches.get_total_items())

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
                    parsed_cves = self.parse_csaf_file(csaf_file)
                    csaf_file.cves = list(parsed_cves.keys())
                    to_store.files[csaf_file.name] = csaf_file
                    to_store.cves.update(parsed_cves)

                self.csaf_store.store(to_store)
        finally:
            self.clean()

    def parse_csaf_file(self, csaf_file: CsafFile) -> CsafCves:
        """Parse CSAF file to CsafCves."""
        product_cpe = {}
        cves = CsafCves()

        if not self.tmp_directory:
            self.logger.error("Missing temporary directory for csaf files")
            raise FileNotFoundError("Missing csaf tmp dir")

        with open(self.tmp_directory / csaf_file.name, "r", encoding="utf-8") as csaf_json:
            csaf = json.load(csaf_json)
            product_cpe = self._parse_product_tree(csaf)
            unfixed_cves = self._parse_vulnerabilities(csaf, product_cpe)
            cves.update(unfixed_cves)
        return cves

    def _parse_product(self, product: str, product_status: str) -> tuple[str, str, str | None]:
        if ":" not in product:
            raise ComponentError(f"Component without ':', '{product}'")

        branch_product, rest = product.split(":", 1)
        pkg = rest
        module = None
        match product_status:
            case "known_affected":
                if "/" in rest:
                    # it's a package with a module or some other identifier
                    module, pkg = rest.split("/", 1)
                    if len(module.split(":")) != 2:
                        # it isn't a module but some other identifier
                        # such as container (rhel-8/python-eventlet) or a java package (com.google.guava/guava)
                        # meaning it is not an rpm and we don't want to process this product
                        raise ComponentError(f"Not RPM component '{product}'")
            case "fixed":
                # already parsed
                # TODO: filter out containers or maven packages once ProdSec starts providing that information in purl
                pass
            case _:
                raise NotImplementedError(f"Unsupported product_status type '{product_status}'")

        return branch_product, pkg, module

    def _parse_vulnerabilities(self, csaf: dict[str, t.Any], product_cpe: dict[str, str]) -> CsafCves:
        cves = CsafCves()
        for vulnerability in csaf["vulnerabilities"]:
            if "cve" not in vulnerability:
                # `vulnerability` can be identified by `cve` or `ids`, we are interested only in those with `cve`
                continue

            product_erratum = self._parse_remediations(vulnerability)
            cve = vulnerability["cve"].upper()
            uniq_products = {}
            for product_status in self.cfg.csaf_product_status_list:
                status_id = CsafProductStatus[product_status.upper()].value
                product_status = product_status.lower()
                for product in vulnerability["product_status"].get(product_status, []):
                    try:
                        branch_product, pkg, module = self._parse_product(product, product_status)
                    except ComponentError as err:
                        self.logger.debug("%s, %s", err, vulnerability["cve"])
                        continue
                    erratum = product_erratum.get(product)
                    csaf_product = CsafProduct(product_cpe[branch_product], pkg, status_id, module, erratum)
                    uniq_products[(product_cpe[branch_product], pkg, module)] = csaf_product

            cves[cve] = CsafProducts(list(uniq_products.values()))

        return cves

    def _parse_remediations(self, vulnerability: dict[str, t.Any]) -> dict[str, str]:
        product_erratum: dict[str, str] = {}
        for remediation in vulnerability.get("remediations", []):
            if remediation.get("category") != "vendor_fix":
                continue
            if found := ERRATUM_RE.findall(remediation.get("url", "")):
                erratum = found[0]
                for product in remediation.get("product_ids", []):
                    # TODO: use only RPM component/product once ProdSec provides purl
                    product_erratum[product] = erratum

        return product_erratum

    def _parse_product_tree(self, csaf: dict[str, t.Any]) -> dict[str, str]:
        product_cpe: dict[str, str] = {}
        for branches in csaf.get("product_tree", {}).get("branches", []):
            self._parse_branches(branches, product_cpe)

        return product_cpe

    def _parse_branches(self, branches: dict[str, t.Any], product_cpe: dict[str, str]) -> None:
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
