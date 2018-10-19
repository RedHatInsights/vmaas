"""Schemas of responses."""
# pylint: disable=C0103
from schema import Or, Optional, Schema

_cves = {
    "cve_list": {
        str: {
            "impact": str,
            "public_date": str,
            "synopsis": str,
            "description": str,
            "modified_date": str,
            Optional("redhat_url"): str,
            "cvss3_score": str,
            Optional("secondary_url"): str,
            "cwe_list": [str],
            "errata_list": [str],
            "package_list": [str],
            "cvss3_metrics": str,
        }
    },
    Optional("modified_since"): str,
    "page": int,
    "page_size": int,
    "pages": int,
}

_pkgs_top = {"package_list": {str: dict}}

_pkgs_list = {
    "summary": str,
    "description": str,
    "repositories": [{"label": str, "name": str, "basearch": str, "releasever": str}],
}

_repos = {
    "repository_list": {
        str: [
            {
                "product": str,
                "releasever": str,
                "name": str,
                "url": str,
                "basearch": Or(str, None),
                "revision": str,
                "label": str,
            }
        ]
    },
    "page": int,
    "page_size": int,
    "pages": int,
}

_errata = {
    "errata_list": {
        str: {
            "updated": str,
            "severity": str,
            "reference_list": [str],
            "issued": str,
            "description": str,
            "solution": Or(str, None),
            "summary": Or(str, None),
            "url": str,
            "synopsis": str,
            "cve_list": [str],
            "bugzilla_list": [str],
            "package_list": [str],
            "type": str,
        }
    },
    Optional("modified_since"): str,
    "page": int,
    "page_size": int,
    "pages": int,
}

_updates_top = {"update_list": {str: dict}}
_updates_top_repolist = {"repository_list": [str], "update_list": {str: dict}}
_updates_top_basearch = {"basearch": str, "update_list": {str: dict}}
_updates_top_releasever = {"releasever": str, "update_list": {str: dict}}
_updates_top_all = {
    "repository_list": [str],
    "releasever": str,
    "basearch": str,
    "update_list": {str: dict},
}

_updates_package = {
    "available_updates": [
        {"basearch": str, "erratum": str, "releasever": str, "repository": str, "package": str}
    ],
    "description": str,
    "summary": str,
}

_updates_package_v2 = {
    "available_updates": [
        {"basearch": str, "erratum": str, "releasever": str, "repository": str, "package": str}
    ]
}

errata_schema = Schema(_errata)
repos_schema = Schema(_repos)
cves_schema = Schema(_cves)
pkgs_top_schema = Schema(_pkgs_top)
pkgs_list_schema = Schema(_pkgs_list)
updates_top_schema = Schema(_updates_top)
updates_top_repolist_schema = Schema(_updates_top_repolist)
updates_top_basearch_schema = Schema(_updates_top_basearch)
updates_top_releasever_schema = Schema(_updates_top_releasever)
updates_top_all_schema = Schema(_updates_top_all)
updates_package_schema = Schema(_updates_package)
updates_package_schema_v2 = Schema(_updates_package_v2)
