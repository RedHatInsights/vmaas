"""
Module containing class for syncing set of GA VEX feed files into the DB.

GA VEX feed format differences from legacy VEX:
- URL: https://security.access.redhat.com/data/csaf/v2/vex-feed/
- Product tree: flat (vendor > product_version only, no product_family/architecture nesting)
- `::` = channel specifier (e.g., `rhel-9.6.z.eus::appstream`), NOT module suffix
- `/` = source component prefix (e.g., `brotli/python3-brotli`)
- Binary RPMs have no architecture; only SRPMs have `.src`
- `+` in release strings is URL-encoded as `%2B`
- Module info for fixed entries is not available (module=None)
- Module info for known_affected/known_not_affected is in entry string prefix
"""

import json
import os
import typing as t
from urllib.parse import unquote

from vmaas.common.batch_list import BatchList
from vmaas.common.config import Config
from vmaas.common.date_utils import parse_datetime
from vmaas.reposcan.database.vexfeed_store import VexFeedStore
from vmaas.reposcan.download.unpacker import TarZstUnpacker
from vmaas.reposcan.redhatcsaf.csaf_controller import CSAF_FAILED_DOWNLOAD
from vmaas.reposcan.redhatcsaf.csaf_controller import CsafController
from vmaas.reposcan.redhatcsaf.csaf_controller import ComponentError
from vmaas.reposcan.redhatcsaf.modeling import CsafCves
from vmaas.reposcan.redhatcsaf.modeling import CsafData
from vmaas.reposcan.redhatcsaf.modeling import CsafFile
from vmaas.reposcan.redhatcsaf.modeling import CsafFiles
from vmaas.reposcan.redhatcsaf.modeling import CsafProduct
from vmaas.reposcan.redhatcsaf.modeling import CsafProductStatus
from vmaas.reposcan.redhatcsaf.modeling import CsafProducts
from vmaas.reposcan.redhatcsaf.modeling import DEFAULT_VARIANT


VEXFEED_BASE_URL = os.getenv(
    "VEXFEED_BASE_URL", "https://security.access.redhat.com/data/csaf/v2/vex-feed/"
)

HARDCODED_ARCH = "x86_64"


class VexFeedController(CsafController):
    """Class for importing/syncing GA VEX feed files into DB.

    Inherits download/archive/signature infrastructure from CsafController,
    overrides parsing logic for the GA VEX format.
    """

    def __init__(self) -> None:
        super().__init__()
        self.base_url = VEXFEED_BASE_URL
        self.csaf_store = VexFeedStore()  # type: ignore[assignment]

    def store(self, sync_all: bool = False) -> None:  # pylint: disable=too-many-branches,too-many-statements
        """Sync GA VEX feed files (cloud/CSV mode only, no IoP tarball-only path)."""
        db_csaf_files = self.csaf_store.csaf_file_map.copy()
        self.logger.info("Checking CSAF index.")
        failed = self._download_index()
        if failed:
            CSAF_FAILED_DOWNLOAD.inc()
            self.logger.warning("Index failed to download.")
            self.clean()
            return

        csaf_files = CsafFiles.from_table_map_and_csv(
            db_csaf_files, self.tmp_directory / "changes.csv"  # type: ignore[arg-type]
        )
        files_to_sync = csaf_files.out_of_date if not sync_all else csaf_files.in_source_files

        batches = BatchList()
        for csaf_file in files_to_sync:
            batches.add_item(csaf_file)

        self.logger.info("%d VEX feed files to sync.", batches.get_total_items())
        self.csaf_store.delete_csaf_files(csaf_files.not_in_source_files)

        try:
            self.logger.info("Downloading CSAF archive.")
            failed = self._download_csaf_archive()
            if failed:
                CSAF_FAILED_DOWNLOAD.inc()
                self.logger.warning("Archive failed to download.")
                self.clean()
                return

            unpacker = TarZstUnpacker(self.tmp_directory / self.archive_name)
            for i, batch in enumerate(batches, 1):
                self.logger.info("Syncing a batch of %d CSAF files [%d/%d]", len(batch), i, len(batches))
                try:
                    unpacker.run({csaf_file.name for csaf_file in batch})
                    failed = self._download_csaf_files(batch)
                    if failed:
                        CSAF_FAILED_DOWNLOAD.inc(len(failed))
                        self.logger.warning("%d files failed to download.", len(failed))
                    to_store = CsafData()
                    for csaf_file in batch:
                        if self.tmp_directory / csaf_file.name in failed:
                            continue
                        parsed_cves = self.parse_csaf_file(csaf_file)
                        csaf_file.cves = list(parsed_cves.keys())
                        to_store.files[csaf_file.name] = csaf_file
                        to_store.cves.update(parsed_cves)
                    self.csaf_store.store(to_store)
                finally:
                    self.clean(batch=batch)
            self.csaf_store.delete_unreferenced_products()
        finally:
            self.clean()

    def parse_csaf_file(self, csaf_file: CsafFile) -> CsafCves:
        """Parse a GA VEX feed JSON file to CsafCves."""
        cves = CsafCves()
        with open(self.tmp_directory / csaf_file.name, "r", encoding="utf-8") as csaf_json:
            csaf = json.load(csaf_json)
            csaf_file.cve_file_timestamp = parse_datetime(
                csaf.get("document", {}).get("tracking", {}).get("current_release_date")
            )
            product_cpe, product_purl = self._parse_product_tree(csaf)
            parsed_cves = self._parse_vulnerabilities(csaf, product_cpe, product_purl)
            cves.update(parsed_cves)
        return cves

    # ------------------------------------------------------------------
    # Product tree parsing (GA format: flat vendor > product_version)
    # ------------------------------------------------------------------

    def _parse_product_tree(  # type: ignore[override]
        self, csaf: dict[str, t.Any]
    ) -> tuple[dict[str, str], dict[str, str]]:
        """Parse product_tree for CPE and PURL mappings.

        GA VEX has a flat product tree (vendor only), so we only need
        CPEs and PURLs — no relationship-based module extraction.
        """
        product_cpe: dict[str, str] = {}
        product_purl: dict[str, str] = {}
        for branches in csaf.get("product_tree", {}).get("branches", []):
            self._parse_branches(branches, product_cpe, product_purl)
        return product_cpe, product_purl

    def _parse_branches(
        self,
        branches: dict[str, t.Any],
        product_cpe: dict[str, str],
        product_purl: dict[str, str],
    ) -> None:
        """Parse branches recursively. GA VEX uses only 'vendor' category at top level."""
        if branches.get("category") not in ("vendor",):
            return
        sub_branches = branches.get("branches", [])
        for sub_branch in sub_branches:
            if "branches" in sub_branch:
                self._parse_branches(sub_branch, product_cpe, product_purl)

            if sub_branch.get("category") not in ("product_name", "product_version"):
                continue

            product = sub_branch.get("product", {})
            product_id = product.get("product_id")
            if product_id is None:
                continue

            if cpe := product.get("product_identification_helper", {}).get("cpe"):
                product_cpe[product_id] = cpe
            if purl := product.get("product_identification_helper", {}).get("purl"):
                product_purl[unquote(product_id)] = purl

    # ------------------------------------------------------------------
    # Vulnerability parsing
    # ------------------------------------------------------------------

    def _parse_vulnerabilities(  # type: ignore[override]  # pylint: disable=arguments-differ
        self,
        csaf: dict[str, t.Any],
        product_cpe: dict[str, str],
        product_purl: dict[str, str],
    ) -> CsafCves:
        cfg = Config()
        cves = CsafCves()
        for vulnerability in csaf.get("vulnerabilities", []):
            if "cve" not in vulnerability:
                continue

            product_erratum = self._parse_remediations(vulnerability)
            cve = vulnerability["cve"].upper()
            uniq_products: dict[tuple[str, str, str | None], CsafProduct] = {}

            for product_status in cfg.csaf_product_status_list:
                status_id = CsafProductStatus[product_status.upper()].value
                product_status = product_status.lower()
                for product in vulnerability.get("product_status", {}).get(product_status, []):
                    try:
                        branch_product, pkg, module, variant_suffix = self._parse_product(
                            product, product_status, product_cpe, product_purl
                        )
                    except ComponentError as err:
                        self.logger.debug("%s, %s", err, vulnerability["cve"])
                        continue

                    if branch_product not in product_cpe:
                        self.logger.debug("No CPE for branch product '%s', %s", branch_product, cve)
                        continue

                    erratum = product_erratum.get(product)
                    csaf_product = CsafProduct(
                        cpe=product_cpe[branch_product],
                        package=pkg,
                        status_id=status_id,
                        module=module,
                        erratum=erratum,
                        variant_suffix=variant_suffix,
                    )
                    uniq_products[(product_cpe[branch_product], pkg, module)] = csaf_product

            cves[cve] = CsafProducts(list(uniq_products.values()))
        return cves

    # ------------------------------------------------------------------
    # Product ID parsing (GA VEX format)
    # ------------------------------------------------------------------

    def _parse_product(  # type: ignore[override]  # pylint: disable=arguments-renamed
        self,
        product: str,
        product_status: str,
        product_cpe: dict[str, str],
        product_purl: dict[str, str],
    ) -> tuple[str, str, str | None, str]:
        """Parse a GA VEX product_id into (branch_product, package, module, variant_suffix).

        GA VEX product_id patterns:

        Fixed (with channel):
            rhel-8.6.0.z.eus::appstream:nodejs/nodejs-0:16.20.2-2.module%2Bel8...
            rhel-9.0.0.z.eus::appstream:nodejs-1:16.20.2-1.el9_0.src

        Fixed (without channel, e.g. rhscl):
            rhscl-3.5.0::el7:rh-nodejs10-nodejs-0:10.21.0-3.el7.src

        known_affected (with module NSVCA):
            rhel-8.8.0.z.eus:nodejs:16:8080020230718141521:63b34585/nodejs

        known_affected (without module, rhscl):
            rhscl-3:rh-nodejs14-nodejs/rh-nodejs14-nodejs

        known_not_affected (with module):
            rhel-8:nodejs:14/nodejs/nodejs-devel
            rhel-8.0.0.z.e4s::appstream:nodejs:14/nodejs/nodejs

        known_not_affected (without module):
            rhel-8.6.0.z.eus::appstream:nodejs/nodejs-debuginfo
        """
        decoded = unquote(product)

        if ":" not in decoded:
            raise ComponentError(f"Component without ':', '{product}'")

        match product_status:
            case "fixed":
                return self._parse_fixed_product(decoded, product_cpe, product_purl)
            case "known_affected":
                return self._parse_known_affected_product(decoded, product_cpe)
            case _:
                raise NotImplementedError(f"Unsupported product_status type '{product_status}'")

    def _parse_fixed_product(
        self,
        product: str,
        product_cpe: dict[str, str],
        product_purl: dict[str, str],
    ) -> tuple[str, str, str | None, str]:
        """Parse a GA VEX fixed product_id.

        Examples:
            rhel-br-8.8.0.z::appstream:nodejs/nodejs-0:16.20.1-1.module+el8...
            rhel-8.6.0.z.eus::appstream:nodejs-0:16.20.2-2.module+el8.6.0+19897+9590a839.src
            rhscl-3.5.0::el7:rh-nodejs10-nodejs-0:10.21.0-3.el7.src
        """
        branch_product = self._find_branch_product(product, product_cpe)
        if branch_product is None:
            raise ComponentError(f"No matching branch product for '{product}'")

        # Extract the component part after the branch product prefix
        component = product[len(branch_product):]
        if component.startswith(":"):
            component = component[1:]

        # Strip source prefix if present (e.g., "nodejs/" in "nodejs/npm-0:...")
        # rsplit: NSVCA paths have 2+ slashes (module:stream:ver:hash/lineage/pkg-NEVRA)
        if "/" in component:
            _source_prefix, pkg = component.rsplit("/", 1)
        else:
            pkg = component

        if not pkg:
            raise ComponentError(f"Empty package in fixed product '{product}'")

        # Validate it's an RPM via PURL (same logic as legacy CsafController):
        # purl not found → skip (not in product tree)
        # purl is pkg:oci/ → skip (container image)
        # purl is rpmmod → skip (module meta-package)
        # purl is pkg:rpm/ (without rpmmod) → valid RPM
        product_ref = component if "/" in component else pkg
        purl = product_purl.get(product_ref, "")
        if not purl or "rpm" not in purl or "rpmmod" in purl:
            raise ComponentError(f"Not RPM component in fixed '{product}'")

        # GA VEX binary RPMs lack architecture — only SRPMs have .src suffix
        if not pkg.endswith(".src"):
            pkg = f"{pkg}.{HARDCODED_ARCH}"

        # Extract variant suffix from base product
        variant_suffix = self._extract_variant_suffix(branch_product)

        # Module is not available for GA VEX fixed entries
        return branch_product, pkg, None, variant_suffix

    def _parse_known_affected_product(
        self,
        product: str,
        product_cpe: dict[str, str],
    ) -> tuple[str, str, str | None, str]:
        """Parse a GA VEX known_affected product_id.

        Examples:
            rhel-8.8.0.z.eus:nodejs:16:8080020230718141521:63b34585/nodejs
            rhel-8:nodejs:14/nodejs.src
            rhscl-3:rh-nodejs14-nodejs/rh-nodejs14-nodejs
        """
        module = None

        # Try to find matching branch product from longest prefix
        branch_product = self._find_branch_product(product, product_cpe)
        if branch_product is None:
            branch_product = product.split(":")[0]
            if branch_product not in product_cpe:
                raise ComponentError(f"No CPE for known_affected product '{product}'")

        if "/" in product:
            # Package is after the last "/", module info is between branch and first "/"
            pkg = product.rsplit("/", 1)[1]
            before_first_slash = product.split("/", 1)[0]
        else:
            # No "/" — entry is a source package (e.g., "rhel-8:vim.src", "cnv-4.12:kubevirt.src")
            after_branch = product[len(branch_product):]
            if after_branch.startswith(":"):
                after_branch = after_branch[1:]
            pkg = after_branch
            if not pkg:
                raise ComponentError(f"Empty package in known_affected product '{product}'")
            return branch_product, pkg, None, DEFAULT_VARIANT

        # Extract module from between branch_product and first /
        before_first_slash = product.split("/", 1)[0]
        after_branch = before_first_slash[len(branch_product):]
        if after_branch.startswith(":"):
            after_branch = after_branch[1:]

        if after_branch:
            # Could be module:stream or module:stream:context:hash
            parts = after_branch.split(":")
            if len(parts) >= 2:
                module = f"{parts[0]}:{parts[1]}"

        return branch_product, pkg, module, DEFAULT_VARIANT

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _find_branch_product(
        self, product: str, product_cpe: dict[str, str]
    ) -> str | None:
        """Find the longest matching branch product prefix in product_cpe keys.

        GA VEX product_ids have the branch product as a prefix. We find
        the longest CPE-bearing prefix that matches.
        """
        best_match: str | None = None
        best_len = 0
        for key in product_cpe:
            if product.startswith(key) and len(key) > best_len:
                # Ensure the match ends at a separator (`:` or end of string)
                next_char_idx = len(key)
                if next_char_idx < len(product) and product[next_char_idx] not in (":", "/"):
                    continue
                best_match = key
                best_len = len(key)
        return best_match

    @staticmethod
    def _extract_variant_suffix(branch_product: str) -> str:
        """Extract variant suffix from branch product.

        The version part always starts with a digit. Compound prefixes
        like ``rhel-br`` are skipped by finding the first dash-separated
        segment that begins with a digit.

        Examples:
            rhel-8.6.0.z.eus::appstream -> 8.6.0.z.eus
            rhel-br-8.8.0.z::appstream  -> 8.8.0.z
            rhel-9.2.0.z.eus            -> 9.2.0.z.eus
            rhscl-3.5.0::el7            -> 3.5.0
            rhel-8                      -> 8
        """
        base = branch_product.split("::")[0]
        parts = base.split("-")
        for i, part in enumerate(parts):
            if part and part[0].isdigit():
                return "-".join(parts[i:])
        return DEFAULT_VARIANT
