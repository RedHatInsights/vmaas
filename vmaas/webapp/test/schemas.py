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
            "cvss2_score": str,
            Optional("secondary_url"): str,
            "cwe_list": [str],
            "errata_list": [str],
            "package_list": [str],
            "source_package_list": [str],
            "cvss3_metrics": str,
            "cvss2_metrics": str,
        }
    },
    Optional("modified_since"): str,
    "page": int,
    "page_size": int,
    "pages": int,
    "last_change": str,
}

_pkgs_top = {"package_list": {str: dict},
             "last_change": str, }

_pkgs_list = {
    "summary": str,
    "description": str,
    "source_package": Or(str, None),
    "package_list": list,
    "repositories": [{"label": str, "name": str, "basearch": str, "releasever": str}],
}

_pkgtree_top = {
    "package_name_list": {str: list},
    "last_change": str,
    "page": int,
    "page_size": int,
    "pages": int,
}

_pkgtree_list = [{
    "nevra": str,
    "summary": str,
    "description": str,
    "first_published": str,
    "repositories": [{
        "label": str,
        "name": str,
        "basearch": str,
        "releasever": str,
        "revision": str,
        Optional("module_name"): str,
        Optional("module_stream"): str,
    }],
    "errata": [{
        "name": str,
        "issued": str,
        "updated": str,
        Optional("cve_list"): [str],
    }],
}]

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
                "last_change": str,
                "label": str,
                "cpes": [str],
                "third_party": bool
            }
        ]
    },
    Optional("modified_since"): Or(str, None),
    "page": int,
    "page_size": int,
    "pages": int,
    "last_change": str,
    "latest_repo_change": str,
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
            "source_package_list": [str],
            "type": str,
            "modules_list": [dict],
            "third_party": bool,
            "requires_reboot": bool,
            "release_versions": [str],
        }
    },
    Optional("modified_since"): str,
    "page": int,
    "page_size": int,
    "pages": int,
    "last_change": str,
}

_updates_top = {"update_list": {str: dict},
                "last_change": str, }
_updates_top_repolist = {"repository_list": [str], "update_list": {str: dict}, "last_change": str, }
_updates_top_basearch = {"basearch": str, "update_list": {str: dict}, "last_change": str, }
_updates_top_releasever = {"releasever": str, "update_list": {str: dict}, "last_change": str, }
_updates_top_all = {
    "repository_list": [str],
    "releasever": str,
    "basearch": str,
    "update_list": {str: dict},
    "modules_list": [dict],
    "last_change": str,
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

_vulnerabilities_response = {
    'cve_list': [Or(str, dict)],
    "manually_fixable_cve_list": [Or(str, dict)],
    'unpatched_cve_list': [Or(str, dict)],
    'last_change': str,
}

_patches_response = {
    'errata_list': [str],
    'last_change': str,
}

_pkg_names_srpm_resp = {
    'last_change': str,
    'srpm_name_list': {str: {str: [str]}}
}

_pkg_names_rpm_resp = {
    'last_change': str,
    'rpm_name_list': {str: [str]}
}

_pkglist = {
    "package_list": [{
        "nevra": str,
        "summary": str,
        "description": str,
        Optional("modified"): str
    }],
    Optional("modified_since"): str,
    "page": int,
    "page_size": int,
    "pages": int,
    "total": int,
    "last_change": str,
}

errata_schema = Schema(_errata)
repos_schema = Schema(_repos)
cves_schema = Schema(_cves)
pkgs_top_schema = Schema(_pkgs_top)
pkgs_list_schema = Schema(_pkgs_list)
pkgtree_top_schema = Schema(_pkgtree_top)
pkgtree_list_schema = Schema(_pkgtree_list)
updates_top_schema = Schema(_updates_top)
updates_top_repolist_schema = Schema(_updates_top_repolist)
updates_top_basearch_schema = Schema(_updates_top_basearch)
updates_top_releasever_schema = Schema(_updates_top_releasever)
updates_top_all_schema = Schema(_updates_top_all)
updates_package_schema = Schema(_updates_package)
updates_package_schema_v2 = Schema(_updates_package_v2)
vulnerabilities_schema = Schema(_vulnerabilities_response)
patches_schema = Schema(_patches_response)
pkg_names_srpm_schema = Schema(_pkg_names_srpm_resp)
pkg_names_rpm_schema = Schema(_pkg_names_rpm_resp)
pkglist_list_schema = Schema(_pkglist)
