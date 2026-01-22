#!/usr/bin/env python3

import argparse
import json
import sys
from pathlib import Path

from urllib.parse import urljoin

from vmaas.common.logging_utils import get_logger
from vmaas.common.logging_utils import init_logging
from vmaas.reposcan.download.downloader import DownloadItem
from vmaas.reposcan.download.downloader import FileDownloader
from vmaas.reposcan.repodata.repomd import RepoMD
from vmaas.reposcan.repodata.repomd import RepoMDTypeNotFound

CA_CERT = "/etc/rhsm/ca/redhat-uep.pem"
ENTITLEMENT_DIR = Path("/etc/pki/entitlement")

LOGGER = get_logger(__name__)


def get_cert():
    cert = key = None
    for pem_file in ENTITLEMENT_DIR.glob("*.pem"):
        pem_file = str(pem_file)
        if pem_file.endswith("-key.pem"):
            key = pem_file
            cert = pem_file.replace("-key", "")
            break
    return cert, key


def preprocess_baseurls(baseurls, output_path):
    repos = []
    for baseurl in baseurls:
        processed = {}
        if not baseurl.endswith("/"):
            baseurl += "/"
        processed["repodata_url"] = urljoin(baseurl, "repodata/")
        target_path = output_path / baseurl.replace("https://cdn.redhat.com/", "") / "repodata"
        target_path.mkdir(parents=True, exist_ok=True)
        processed["target_path"] = target_path
        repos.append(processed)
    return repos


def download_baseurls(baseurls, output_path):
    repos = preprocess_baseurls(baseurls, output_path)
    cert, key = get_cert()
    downloader = FileDownloader()

    for repo in repos:
        item = DownloadItem(
            source_url=urljoin(repo["repodata_url"], "repomd.xml"),
            target_path=repo["target_path"] / "repomd.xml",
            ca_cert=CA_CERT,
            cert=cert,
            key=key
        )
        downloader.add(item)
    downloader.run()

    for repo in repos:
        repomd = RepoMD(repo["target_path"] / "repomd.xml")
        try:
            primary = repomd.get_metadata("primary_db")["location"]
        except RepoMDTypeNotFound:
            primary = repomd.get_metadata("primary")["location"]
        try:
            updateinfo = repomd.get_metadata("updateinfo")["location"]
        except RepoMDTypeNotFound:
            updateinfo = None
        try:
            modules = repomd.get_metadata("modules")["location"]
        except RepoMDTypeNotFound:
            modules = None
        for md_file in (primary, updateinfo, modules):
            if not md_file:
                continue
            filename = Path(md_file).name
            item = DownloadItem(
                source_url=urljoin(repo["repodata_url"], filename),
                target_path=repo["target_path"] / filename,
                ca_cert=CA_CERT,
                cert=cert,
                key=key
            )
            downloader.add(item)
    downloader.run()


def download_repolist(repolist, output_path):
    baseurls = set()
    for repo_group in repolist:
        for _, product in repo_group["products"].items():
            for _, content_set in product["content_sets"].items():
                for basearch in content_set["basearch"]:
                    for releasever in content_set["releasever"]:
                        baseurls.add(content_set["baseurl"].replace("$basearch", basearch).replace("$releasever", releasever))
    download_baseurls(baseurls, output_path)


def main():
    init_logging()
    parser = argparse.ArgumentParser(description="Download repository metadata from JSON repolist")
    parser.add_argument("repolist_file", type=str, help="Path to JSON repolist")
    parser.add_argument("output_dir", type=str, help="Path to output directory")

    args = parser.parse_args()

    repolist_file = Path(args.repolist_file)
    output_path = Path(args.output_dir)

    if not repolist_file.exists():
        LOGGER.error("Error: Repolist file '%s' does not exist", repolist_file)
        sys.exit(1)

    if not repolist_file.is_file():
        LOGGER.error("Error: '%s' is not a file", repolist_file)
        sys.exit(1)

    try:
        with open(repolist_file, "r") as f:
            repolist = json.load(f)
    except Exception as e:
        LOGGER.error("Error: Failed to read JSON file: %s", e)
        sys.exit(1)

    download_repolist(repolist, output_path)


if __name__ == '__main__':
    main()
