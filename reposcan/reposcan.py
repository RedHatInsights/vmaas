#!/usr/bin/python3

import os
import sys
import tempfile
from urllib.parse import urljoin

from download.downloader import FileDownloader, DownloadItem
from download.unpacker import FileUnpacker
from repodata.repomd import RepoMD
from repodata.primary import PrimaryMD

REPODATA_DIR = "repodata/"


def download_repodata(repo_url):
    tmp_directory = tempfile.mkdtemp(prefix="repo-")
    repodata_url = urljoin(repo_url, REPODATA_DIR)
    repomd_url = urljoin(repodata_url, "repomd.xml")
    print("Repomd URL: %s" % repomd_url)
    target_repomd_path = os.path.join(tmp_directory, "repomd.xml")

    # Get repomd
    downloader = FileDownloader()
    unpacker = FileUnpacker()
    downloader.add(DownloadItem(
        source_url=repomd_url,
        target_path=target_repomd_path
    ))
    downloader.run()
    repomd = RepoMD(target_repomd_path)

    md_files = {}
    # Get primary and updateinfo
    for md_type in ("primary", "updateinfo"):
        md = repomd.get_metadata(md_type)
        md_url = urljoin(repo_url, md["location"])
        downloader.add(DownloadItem(
            source_url=md_url,
            target_path=os.path.join(tmp_directory, os.path.basename(md["location"]))
        ))
        unpacker.add(os.path.join(tmp_directory, os.path.basename(md["location"])))
        # FIXME: this should be done in different place
        md_files[md_type] = os.path.join(tmp_directory, os.path.basename(md["location"])).rsplit(".", maxsplit=1)[0]
    downloader.run()
    unpacker.run()

    primary = PrimaryMD(md_files["primary"])
    print(primary.get_package_count())

if __name__ == '__main__':
    repo_url = sys.argv[1]
    print("Repo URL: %s" % repo_url)
    download_repodata(repo_url)
