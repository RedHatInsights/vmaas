#!/usr/libexec/platform-python
# mypy: disable-error-code="import-not-found"
# pylint: disable=import-error
"""
External script to generate system package profile using DNF.

This script is executed using platform Python and not imported directly
due to incompatibility between platform Python version of the libdnf (and others) - 3.6
and Python version running the application - 3.12.

This code might be included in the application after the running image is upgraded from UBI 8.
"""
import json
import os
import sys

import dnf

DNF_CACHEDIR = os.getenv("DNF_CACHEDIR", "")
DNF_REPOS = json.loads(os.getenv("DNF_REPOS", "[]"))
DNF_PLATFORM_ID = os.getenv("DNF_PLATFORM_ID", "")


def _write_cert(label: str, cert_type: str, content: str) -> str:
    cert_path = os.path.join(DNF_CACHEDIR, f"{label}-{cert_type}")
    with open(cert_path, "w", encoding='utf8') as cert_file:
        cert_file.write(content)
    return cert_path


def main() -> None:
    """Script entrypoint."""
    if not all([DNF_CACHEDIR, DNF_REPOS, DNF_PLATFORM_ID]):
        print("Some config ENV is not set!", file=sys.stderr)
        sys.exit(1)

    base = dnf.Base()
    base.conf.cachedir = DNF_CACHEDIR
    base.conf.installroot = DNF_CACHEDIR
    base.conf.substitutions["arch"] = "x86_64"
    base.conf.module_platform_id = DNF_PLATFORM_ID
    for label, url, ca_cert, cert, key in DNF_REPOS:
        ca_cert_path = _write_cert(label, "ca_cert", ca_cert)
        cert_path = _write_cert(label, "cert", cert)
        key_path = _write_cert(label, "key", key)
        base.repos.add_new_repo(label,
                                base.conf,
                                baseurl=[url],
                                sslcacert=ca_cert_path,
                                sslclientcert=cert_path,
                                sslclientkey=key_path)
    base.fill_sack(load_system_repo=False, load_available_repos=True)
    base.install_specs(["kernel", "@core", "@base"])
    base.resolve()
    system_profile = {"package_list": [f"{pkg.name}-{pkg.epoch}:{pkg.version}-{pkg.release}.{pkg.arch}"
                                       for pkg in base.transaction.install_set]}
    base.close()

    print(json.dumps(system_profile))


if __name__ == "__main__":
    main()
