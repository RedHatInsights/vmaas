"""
Definitions for apispec documentation.
"""

import os
from apispec import APISpec

VMAAS_VERSION = os.getenv("VMAAS_VERSION", "unknown")
SPEC = APISpec(
    title='VMaaS Reposcan',
    version=VMAAS_VERSION,
    plugins=(
        'apispec.ext.tornado',
    ),
    basePath="/api/v1",
)


def setup_apispec(handlers):
    """Setup definitions and handlers for apispec."""
    SPEC.definition("TaskStatusResponse", properties={"running": {"type": "boolean"},
                                                      "task_type": {"type": "string", "example": "Sync CVEs"}})
    SPEC.definition("TaskStartResponse", properties={"success": {"type": "boolean"},
                                                     "msg": {"type": "string", "example": "Repo sync task started."}})
    SPEC.definition("PkgTreeDownloadResponse", properties={
        "timestamp": {
            "type": "string",
            "example": "2018-08-27T18:24:51.840698+00:00"
        },
        "packages": {
            "type": "object",
            "properties": {
                "kernel": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "nevra": {
                                "type": "string",
                                "example": "kernel-2.6.32-71.el6.x86_64"
                            },
                            "first_published": {
                                "type": "string",
                                "example": "2010-11-10T00:00:00+00:00"
                            },
                            "repositories": {
                                "type": "object",
                                "properties": {
                                    "label": {
                                        "type": "string",
                                        "example": "rhel-6-workstation-rpms"
                                    },
                                    "name": {
                                        "type": "string",
                                        "example": "Red Hat Enterprise Linux 6 Workstation (RPMs)"
                                    },
                                    "arch": {
                                        "type": "string",
                                        "example": "x86_64"
                                    },
                                    "releasever": {
                                        "type": "string",
                                        "example": "6Workstation"
                                    },
                                    "revision": {
                                        "type": "string",
                                        "example": "2018-08-20T15:11:29+00:00"
                                    }
                                }
                            },
                            "errata": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "example": "RHSA-2010:0842"
                                    },
                                    "issued": {
                                        "type": "string",
                                        "example": "2010-11-10T00:00:00+00:00"
                                    },
                                    "cve_list": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "example": "CVE-2010-3437"
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    })
    SPEC.definition("DbChangeResponse", properties={
        "pkgtree_change": {
            "type": "string",
            "example": "2010-11-10T00:00:00+00:00"
        }
    })
    # Register public API handlers to apispec
    for handler in handlers:
        if handler[0].startswith(('/api/')):
            SPEC.add_path(urlspec=handler)
