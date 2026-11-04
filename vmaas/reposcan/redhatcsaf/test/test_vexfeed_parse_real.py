"""Unit tests for VexFeedController._parse_product using real product_id strings.

Every product_id is taken from real GA VEX feed files (CVE-2023-0049, CVE-2024-22019).
Tests do NOT require a database connection.
"""
# pylint: disable=line-too-long,too-many-lines,protected-access,redefined-outer-name,missing-function-docstring

import pathlib
from unittest.mock import patch, MagicMock
from urllib.parse import unquote

import pytest

from vmaas.reposcan.redhatcsaf.modeling import DEFAULT_VARIANT
from vmaas.reposcan.redhatcsaf.vexfeed_controller import VexFeedController


# ------------------------------------------------------------------
# CPE mappings for all branch products used in tests
# ------------------------------------------------------------------
PRODUCT_CPE = {
    "openshift-data-foundation-4.12.z": "cpe:/a:redhat:openshift_data_foundation:4",
    "rhel-8.10.0": "cpe:/a:redhat:enterprise_linux:8",
    "rhel-8.2.0.z.aus": "cpe:/a:redhat:rhel_aus:8.2",
    "rhel-8.4.0.z.eus": "cpe:/a:redhat:rhel_eus:8.4",
    "rhel-8.6.0.z.aus": "cpe:/a:redhat:rhel_aus:8.6",
    "rhel-8.6.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:8.6::appstream",
    "rhel-8.8.0.z.eus": "cpe:/a:redhat:rhel_eus:8.8",
    "rhel-8.8.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:8.8::appstream",
    "rhel-8.9.0.z::appstream": "cpe:/a:redhat:enterprise_linux:8::appstream",
    "rhel-9.0.0.z.eus": "cpe:/a:redhat:rhel_eus:9.0",
    "rhel-9.0.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.0::appstream",
    "rhel-9.2.0.z.eus": "cpe:/a:redhat:rhel_eus:9.2",
    "rhel-9.2.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.2::appstream",
    "rhel-9.3.0.z": "cpe:/a:redhat:enterprise_linux:9",
    "rhel-9.3.0.z::appstream": "cpe:/a:redhat:enterprise_linux:9::appstream",
    "rhel-br-8.6.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:8.6::appstream",
    "rhel-br-8.8.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:8.8::appstream",
    "rhel-br-9.0.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.0::appstream",
    "rhel-br-9.2.0.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.2::appstream",
    "rhscl-3.8.0::el7": "cpe:/a:redhat:rhel_software_collections:3::el7",
    "rhel-6-els.els": "cpe:/o:redhat:rhel_els:6",
    "rhel-7.els": "cpe:/o:redhat:rhel_els:7",
    "rhel-8": "cpe:/a:redhat:enterprise_linux:8",
    "rhel-9": "cpe:/a:redhat:enterprise_linux:9",
    "cnv-4.12": "cpe:/a:redhat:container_native_virtualization:4.12",
    "cnv-4.13": "cpe:/a:redhat:container_native_virtualization:4.13",
    "cnv-4.14": "cpe:/a:redhat:container_native_virtualization:4.14",
    "cnv-4.15": "cpe:/a:redhat:container_native_virtualization:4.15",
    "cnv-4.16": "cpe:/a:redhat:container_native_virtualization:4.16",
    "cnv-4.17": "cpe:/a:redhat:container_native_virtualization:4.17",
    "ocp-tools-4.11": "cpe:/a:redhat:ocp_tools:4.11",
    "ocp-tools-4.12": "cpe:/a:redhat:ocp_tools:4.12",
    "ocp-tools-4.14": "cpe:/a:redhat:ocp_tools:4.14",
    "ocp-tools-4.15": "cpe:/a:redhat:ocp_tools:4.15",
    "ocp-tools-4.15::el8": "cpe:/a:redhat:ocp_tools:4.15::el8",
    "openshift-4.11::el8": "cpe:/a:redhat:openshift:4.11::el8",
    "openshift-4.12.z": "cpe:/a:redhat:openshift:4.12",
    "openshift-4.12::el8": "cpe:/a:redhat:openshift:4.12::el8",
    "openshift-4.13.z": "cpe:/a:redhat:openshift:4.13",
    "openshift-4.13::el8": "cpe:/a:redhat:openshift:4.13::el8",
    "openshift-4.13::el9": "cpe:/a:redhat:openshift:4.13::el9",
    "openshift-4.14.z": "cpe:/a:redhat:openshift:4.14",
    "openshift-4.14::el8": "cpe:/a:redhat:openshift:4.14::el8",
    "openshift-4.14::el9": "cpe:/a:redhat:openshift:4.14::el9",
    "openshift-4.15": "cpe:/a:redhat:openshift:4.15",
    "openshift-4.15.z": "cpe:/a:redhat:openshift:4.15",
    "openshift-4.15::el8": "cpe:/a:redhat:openshift:4.15::el8",
    "openshift-4.15::el9": "cpe:/a:redhat:openshift:4.15::el9",
    "openshift-4.16.z": "cpe:/a:redhat:openshift:4.16",
    "openshift-4.16::el9": "cpe:/a:redhat:openshift:4.16::el9",
    "openshift-4.17": "cpe:/a:redhat:openshift:4.17",
    "openshift-4.17::el9": "cpe:/a:redhat:openshift:4.17::el9",
    "openshift-4.18": "cpe:/a:redhat:openshift:4.18",
    "quay-3.10": "cpe:/a:redhat:quay:3.10",
    "quay-3.11": "cpe:/a:redhat:quay:3.11",
    "quay-3.12": "cpe:/a:redhat:quay:3.12",
    "quay-3.13": "cpe:/a:redhat:quay:3.13",
    "quay-3.9": "cpe:/a:redhat:quay:3.9",
    "rhel-10.0.z.eus": "cpe:/o:redhat:enterprise_linux_eus:10.0",
    "rhel-10.1": "cpe:/o:redhat:enterprise_linux:10.1",
    "rhel-10.1.z": "cpe:/o:redhat:enterprise_linux:10.1",
    "rhel-10.2": "cpe:/o:redhat:enterprise_linux:10.2",
    "rhel-7.9.z": "cpe:/a:redhat:rhel_extras_other:7",
    "rhel-8.10.z": "cpe:/a:redhat:rhel_e6s:8.10",
    "rhel-8.2.0.z.aus::appstream": "cpe:/a:redhat:rhel_aus:8.2::appstream",
    "rhel-8.2.0.z.e4s::appstream": "cpe:/a:redhat:rhel_e4s:8.2::appstream",
    "rhel-8.2.0.z.tus::appstream": "cpe:/a:redhat:rhel_tus:8.2::appstream",
    "rhel-8.4.0.z.aus::appstream": "cpe:/a:redhat:rhel_aus:8.4::appstream",
    "rhel-8.4.0.z.e4s::appstream": "cpe:/a:redhat:rhel_e4s:8.4::appstream",
    "rhel-8.4.0.z.tus::appstream": "cpe:/a:redhat:rhel_tus:8.4::appstream",
    "rhel-8.9.0.z": "cpe:/a:redhat:enterprise_linux:8",
    "rhel-9.4.z.eus": "cpe:/a:redhat:rhel_eus:9.4",
    "rhel-9.5": "cpe:/a:redhat:enterprise_linux:9",
    "rhel-9.5.z": "cpe:/a:redhat:enterprise_linux:9",
    "rhel-9.6": "cpe:/a:redhat:enterprise_linux:9",
    "rhel-br-8.2.0.z.e4s::appstream": "cpe:/a:redhat:rhel_e4s:8.2::appstream",
    "rhel-br-8.2.0.z.tus::appstream": "cpe:/a:redhat:rhel_tus:8.2::appstream",
    "rhel-br-8.4.0.z.e4s::appstream": "cpe:/a:redhat:rhel_e4s:8.4::appstream",
    "rhel-br-8.4.0.z.tus::appstream": "cpe:/a:redhat:rhel_tus:8.4::appstream",
    "rhpm-0.1": "cpe:/a:redhat:openshift_power_monitoring",
    "openshift-logging-5.8::el9": "cpe:/a:redhat:logging:5.8::el9",
    "rhel-7-els.els": "cpe:/o:redhat:rhel_els:7",
    "rhel-8.2.0.z.aus::baseos": "cpe:/o:redhat:rhel_aus:8.2::baseos",
    "rhel-8.2.0.z.e4s::baseos": "cpe:/o:redhat:rhel_e4s:8.2::baseos",
    "rhel-8.2.0.z.tus::baseos": "cpe:/o:redhat:rhel_tus:8.2::baseos",
    "rhel-8.2.0.z.tus::nfv": "cpe:/a:redhat:rhel_tus:8.2::nfv",
    "rhel-8.2.0.z.tus::realtime": "cpe:/a:redhat:rhel_tus:8.2::realtime",
    "rhel-8.4.0.z.aus::baseos": "cpe:/o:redhat:rhel_aus:8.4::baseos",
    "rhel-8.4.0.z.e4s::baseos": "cpe:/o:redhat:rhel_e4s:8.4::baseos",
    "rhel-8.4.0.z.tus::baseos": "cpe:/o:redhat:rhel_tus:8.4::baseos",
    "rhel-8.4.0.z.tus::nfv": "cpe:/a:redhat:rhel_tus:8.4::nfv",
    "rhel-8.4.0.z.tus::realtime": "cpe:/a:redhat:rhel_tus:8.4::realtime",
    "rhel-8.6.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:8.6::baseos",
    "rhel-8.6.0.z.eus::crb": "cpe:/a:redhat:rhel_eus:8.6::crb",
    "rhel-8.8.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:8.8::baseos",
    "rhel-8.8.0.z.eus::crb": "cpe:/a:redhat:rhel_eus:8.8::crb",
    "rhel-8.9.0.z::baseos": "cpe:/o:redhat:enterprise_linux:8::baseos",
    "rhel-8.9.0.z::crb": "cpe:/a:redhat:enterprise_linux:8::crb",
    "rhel-8.9.0.z::nfv": "cpe:/a:redhat:enterprise_linux:8::nfv",
    "rhel-8.9.0.z::realtime": "cpe:/a:redhat:enterprise_linux:8::realtime",
    "rhel-9.0.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:9.0::baseos",
    "rhel-9.0.0.z.eus::crb": "cpe:/a:redhat:rhel_eus:9.0::crb",
    "rhel-9.0.0.z.eus::nfv": "cpe:/a:redhat:rhel_eus:9.0::nfv",
    "rhel-9.0.0.z.eus::realtime": "cpe:/a:redhat:rhel_eus:9.0::realtime",
    "rhel-9.2.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:9.2::baseos",
    "rhel-9.2.0.z.eus::crb": "cpe:/a:redhat:rhel_eus:9.2::crb",
    "rhel-9.2.0.z.eus::nfv": "cpe:/a:redhat:rhel_eus:9.2::nfv",
    "rhel-9.2.0.z.eus::realtime": "cpe:/a:redhat:rhel_eus:9.2::realtime",
    "rhel-9.3.0.z::baseos": "cpe:/o:redhat:enterprise_linux:9::baseos",
    "rhel-9.3.0.z::crb": "cpe:/a:redhat:enterprise_linux:9::crb",
    "rhel-9.3.0.z::nfv": "cpe:/a:redhat:enterprise_linux:9::nfv",
    "rhel-9.3.0.z::realtime": "cpe:/a:redhat:enterprise_linux:9::realtime",
    "rhel-br-8.2.0.z.e4s::baseos": "cpe:/o:redhat:rhel_e4s:8.2::baseos",
    "rhel-br-8.4.0.z.e4s::baseos": "cpe:/o:redhat:rhel_e4s:8.4::baseos",
    "rhel-br-8.4.0.z.tus::baseos": "cpe:/o:redhat:rhel_tus:8.4::baseos",
    "rhel-br-8.4.0.z.tus::nfv": "cpe:/a:redhat:rhel_tus:8.4::nfv",
    "rhel-br-8.4.0.z.tus::realtime": "cpe:/a:redhat:rhel_tus:8.4::realtime",
    "rhel-br-8.6.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:8.6::baseos",
    "rhel-br-8.6.0.z.eus::crb": "cpe:/a:redhat:rhel_eus:8.6::crb",
    "rhel-br-8.8.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:8.8::baseos",
    "rhel-br-8.8.0.z.eus::crb": "cpe:/a:redhat:rhel_eus:8.8::crb",
    "rhel-br-9.0.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:9.0::baseos",
    "rhel-br-9.2.0.z.eus::baseos": "cpe:/o:redhat:rhel_eus:9.2::baseos",
    "rhel-br-9.2.0.z.eus::crb": "cpe:/a:redhat:rhel_eus:9.2::crb",
    "rhel-br-9.2.0.z.eus::nfv": "cpe:/a:redhat:rhel_eus:9.2::nfv",
    "rhel-br-9.2.0.z.eus::realtime": "cpe:/a:redhat:rhel_eus:9.2::realtime",
    "rhev-m-4::el8": "cpe:/o:redhat:rhev_hypervisor:4.4::el8",
    "hummingbird-1": "cpe:/a:redhat:hummingbird:1",
    "rhel-8.10.z::appstream": "cpe:/a:redhat:enterprise_linux:8::appstream",
    "rhel-8.10.z::crb": "cpe:/a:redhat:enterprise_linux:8::crb",
    "rhel-9.4.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.4::appstream",
    "rhel-9.4.z.eus::crb": "cpe:/a:redhat:rhel_eus:9.4::crb",
    "rhel-9.6.z.eus": "cpe:/a:redhat:rhel_eus:9.6",
    "rhel-9.6.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.6::appstream",
    "rhel-9.6.z.eus::crb": "cpe:/a:redhat:rhel_eus:9.6::crb",
    "rhel-9.7.z": "cpe:/a:redhat:enterprise_linux:9",
    "rhel-9.7.z::appstream": "cpe:/a:redhat:enterprise_linux:9::appstream",
    "rhel-9.7.z::crb": "cpe:/a:redhat:enterprise_linux:9::crb",
    "rhel-9.7::appstream": "cpe:/a:redhat:enterprise_linux:9::appstream",
    "rhel-9.8": "cpe:/a:redhat:enterprise_linux:9",
    "rhel-br-9.4.z.eus::appstream": "cpe:/a:redhat:rhel_eus:9.4::appstream",
    "rhel-br-9.4.z.eus::crb": "cpe:/a:redhat:rhel_eus:9.4::crb",
    "rhel-br-9.6.z::crb": "cpe:/a:redhat:enterprise_linux:9::crb",
    "rhos_devspaces-3.21": "cpe:/a:redhat:openshift_devspaces:3.21",
    "rhos_devspaces-3.22": "cpe:/a:redhat:openshift_devspaces:3.22",
    "rhos_devspaces-3.23": "cpe:/a:redhat:openshift_devspaces:3.23",
    "rhos_devspaces-3.25::el9": "cpe:/a:redhat:openshift_devspaces:3.25::el9",
}

PACKAGE_PURL = {
    "nodejs-0:16-8060020240318185600.ad008a3a.src": "pkg:rpm/redhat/nodejs@16-8060020240318185600.ad008a3a?arch=src&epoch=0",
    "nodejs-0:16.20.2-4.module+el8.6.0+21547+94389150.src": "pkg:rpm/redhat/nodejs@16.20.2-4.module%2Bel8.6.0%2B21547%2B94389150?arch=src&epoch=0",
    "nodejs-0:16.20.2-4.module+el8.8.0+21546+ecd4bb56.src": "pkg:rpm/redhat/nodejs@16.20.2-4.module%2Bel8.8.0%2B21546%2Becd4bb56?arch=src&epoch=0",
    "nodejs-0:16.20.2-4.module+el8.9.0+21536+8fdee1fb.src": "pkg:rpm/redhat/nodejs@16.20.2-4.module%2Bel8.9.0%2B21536%2B8fdee1fb?arch=src&epoch=0",
    "nodejs-0:18.19.1-1.module+el8.8.0+21592+14a8b93e.src": "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel8.8.0%2B21592%2B14a8b93e?arch=src&epoch=0",
    "nodejs-0:18.19.1-1.module+el8.9.0+21387+21356dec.src": "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel8.9.0%2B21387%2B21356dec?arch=src&epoch=0",
    "nodejs-0:18.19.1-1.module+el9.2.0+21594+a052107e.src": "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel9.2.0%2B21594%2Ba052107e?arch=src&epoch=0",
    "nodejs-0:18.19.1-1.module+el9.3.0+21388+22892fb9.src": "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel9.3.0%2B21388%2B22892fb9?arch=src&epoch=0",
    "nodejs-0:20.11.1-1.module+el8.9.0+21380+12032667.src": "pkg:rpm/redhat/nodejs@20.11.1-1.module%2Bel8.9.0%2B21380%2B12032667?arch=src&epoch=0",
    "nodejs-0:20.11.1-1.module+el9.3.0+21385+bac43d5a.src": "pkg:rpm/redhat/nodejs@20.11.1-1.module%2Bel9.3.0%2B21385%2Bbac43d5a?arch=src&epoch=0",
    "nodejs-1:16.20.2-4.el9_0.src": "pkg:rpm/redhat/nodejs@16.20.2-4.el9_0?arch=src&epoch=1",
    "nodejs-1:16.20.2-4.el9_2.src": "pkg:rpm/redhat/nodejs@16.20.2-4.el9_2?arch=src&epoch=1",
    "nodejs-1:16.20.2-4.el9_3.src": "pkg:rpm/redhat/nodejs@16.20.2-4.el9_3?arch=src&epoch=1",
    "nodejs/nodejs-0:16.20.2-4.module%2Bel8.6.0%2B21547%2B94389150":
        "pkg:rpm/redhat/nodejs@16.20.2-4.module%2Bel8.6.0%2B21547%2B94389150?epoch=0&upstream=nodejs",
    "nodejs/nodejs-0:16.20.2-4.module%2Bel8.8.0%2B21546%2Becd4bb56":
        "pkg:rpm/redhat/nodejs@16.20.2-4.module%2Bel8.8.0%2B21546%2Becd4bb56?epoch=0&upstream=nodejs",
    "nodejs/nodejs-0:18.19.1-1.module%2Bel8.8.0%2B21592%2B14a8b93e":
        "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel8.8.0%2B21592%2B14a8b93e?epoch=0&upstream=nodejs",
    "nodejs/nodejs-0:18.19.1-1.module%2Bel8.9.0%2B21387%2B21356dec":
        "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel8.9.0%2B21387%2B21356dec?epoch=0&upstream=nodejs",
    "nodejs/nodejs-0:18.19.1-1.module%2Bel9.2.0%2B21594%2Ba052107e":
        "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel9.2.0%2B21594%2Ba052107e?epoch=0&upstream=nodejs",
    "nodejs/nodejs-0:18.19.1-1.module%2Bel9.3.0%2B21388%2B22892fb9":
        "pkg:rpm/redhat/nodejs@18.19.1-1.module%2Bel9.3.0%2B21388%2B22892fb9?epoch=0&upstream=nodejs",
    "nodejs/nodejs-0:20.11.1-1.module%2Bel8.9.0%2B21380%2B12032667":
        "pkg:rpm/redhat/nodejs@20.11.1-1.module%2Bel8.9.0%2B21380%2B12032667?epoch=0&upstream=nodejs",
    "nodejs/nodejs-0:20.11.1-1.module%2Bel9.3.0%2B21385%2Bbac43d5a":
        "pkg:rpm/redhat/nodejs@20.11.1-1.module%2Bel9.3.0%2B21385%2Bbac43d5a?epoch=0&upstream=nodejs",
    "nodejs/nodejs-1:16.20.2-4.el9_0": "pkg:rpm/redhat/nodejs@16.20.2-4.el9_0?epoch=1&upstream=nodejs",
    "nodejs/nodejs-1:16.20.2-4.el9_2": "pkg:rpm/redhat/nodejs@16.20.2-4.el9_2?epoch=1&upstream=nodejs",
    "nodejs/nodejs-1:16.20.2-4.el9_3": "pkg:rpm/redhat/nodejs@16.20.2-4.el9_3?epoch=1&upstream=nodejs",
    "nodejs/nodejs-debuginfo": "pkg:rpm/redhat/nodejs-debuginfo?upstream=nodejs",
    "nodejs/nodejs-debugsource": "pkg:rpm/redhat/nodejs-debugsource?upstream=nodejs",
    "nodejs/nodejs-devel": "pkg:rpm/redhat/nodejs-devel?upstream=nodejs",
    "nodejs/nodejs-devel-debuginfo": "pkg:rpm/redhat/nodejs-devel-debuginfo?upstream=nodejs",
    "nodejs/nodejs-docs": "pkg:rpm/redhat/nodejs-docs?upstream=nodejs",
    "nodejs/nodejs-full-i18n": "pkg:rpm/redhat/nodejs-full-i18n?upstream=nodejs",
    "nodejs/nodejs-libs": "pkg:rpm/redhat/nodejs-libs?upstream=nodejs",
    "nodejs/nodejs-libs-1:16.20.2-4.el9_0": "pkg:rpm/redhat/nodejs-libs@16.20.2-4.el9_0?epoch=1&upstream=nodejs",
    "nodejs/nodejs-libs-1:16.20.2-4.el9_2": "pkg:rpm/redhat/nodejs-libs@16.20.2-4.el9_2?epoch=1&upstream=nodejs",
    "nodejs/nodejs-libs-1:16.20.2-4.el9_3": "pkg:rpm/redhat/nodejs-libs@16.20.2-4.el9_3?epoch=1&upstream=nodejs",
    "nodejs/nodejs-libs-debuginfo": "pkg:rpm/redhat/nodejs-libs-debuginfo?upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel8.6.0%2B19765%2B366b9144":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel8.6.0%2B19765%2B366b9144?epoch=0&upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel8.8.0%2B19757%2B8ca87034":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel8.8.0%2B19757%2B8ca87034?epoch=0&upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel8.8.0%2B19764%2B7eed1ca3":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel8.8.0%2B19764%2B7eed1ca3?epoch=0&upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel8.9.0%2B20473%2Bc4e3d824":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel8.9.0%2B20473%2Bc4e3d824?epoch=0&upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel8.9.0%2B21190%2B5ebd2c33":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel8.9.0%2B21190%2B5ebd2c33?epoch=0&upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel9.2.0.z%2B19753%2B58118bc0":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel9.2.0.z%2B19753%2B58118bc0?epoch=0&upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel9.3.0%2B19762%2Bd716bf3b":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel9.3.0%2B19762%2Bd716bf3b?epoch=0&upstream=nodejs",
    "nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel9.3.0.z%2B20478%2B84a9f781":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel9.3.0.z%2B20478%2B84a9f781?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-0:2021.06-4.module%2Bel8.7.0%2B15582%2B19c314fa":
        "pkg:rpm/redhat/nodejs-packaging@2021.06-4.module%2Bel8.7.0%2B15582%2B19c314fa?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-0:2021.06-4.module%2Bel8.9.0%2B19519%2Be25b965a":
        "pkg:rpm/redhat/nodejs-packaging@2021.06-4.module%2Bel8.9.0%2B19519%2Be25b965a?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-0:2021.06-4.module%2Bel8.9.0%2B21190%2B5ebd2c33":
        "pkg:rpm/redhat/nodejs-packaging@2021.06-4.module%2Bel8.9.0%2B21190%2B5ebd2c33?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-0:2021.06-4.module%2Bel9.1.0%2B15718%2Be52ec601":
        "pkg:rpm/redhat/nodejs-packaging@2021.06-4.module%2Bel9.1.0%2B15718%2Be52ec601?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-0:2021.06-4.module%2Bel9.3.0%2B19518%2B63aad52d":
        "pkg:rpm/redhat/nodejs-packaging@2021.06-4.module%2Bel9.3.0%2B19518%2B63aad52d?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-0:26-1.module%2Bel8.6.0%2B19856%2Bc0c87259":
        "pkg:rpm/redhat/nodejs-packaging@26-1.module%2Bel8.6.0%2B19856%2Bc0c87259?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-0:26-1.module%2Bel8.8.0%2B19857%2B6d2a104d":
        "pkg:rpm/redhat/nodejs-packaging@26-1.module%2Bel8.8.0%2B19857%2B6d2a104d?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-bundler-0:2021.06-4.module%2Bel8.7.0%2B15582%2B19c314fa":
        "pkg:rpm/redhat/nodejs-packaging-bundler@2021.06-4.module%2Bel8.7.0%2B15582%2B19c314fa?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-bundler-0:2021.06-4.module%2Bel8.9.0%2B19519%2Be25b965a":
        "pkg:rpm/redhat/nodejs-packaging-bundler@2021.06-4.module%2Bel8.9.0%2B19519%2Be25b965a?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-bundler-0:2021.06-4.module%2Bel8.9.0%2B21190%2B5ebd2c33":
        "pkg:rpm/redhat/nodejs-packaging-bundler@2021.06-4.module%2Bel8.9.0%2B21190%2B5ebd2c33?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-bundler-0:2021.06-4.module%2Bel9.1.0%2B15718%2Be52ec601":
        "pkg:rpm/redhat/nodejs-packaging-bundler@2021.06-4.module%2Bel9.1.0%2B15718%2Be52ec601?epoch=0&upstream=nodejs",
    "nodejs/nodejs-packaging-bundler-0:2021.06-4.module%2Bel9.3.0%2B19518%2B63aad52d":
        "pkg:rpm/redhat/nodejs-packaging-bundler@2021.06-4.module%2Bel9.3.0%2B19518%2B63aad52d?epoch=0&upstream=nodejs",
    "nodejs/npm-0:10.2.4-1.18.19.1.1.module%2Bel8.8.0%2B21592%2B14a8b93e":
        "pkg:rpm/redhat/npm@10.2.4-1.18.19.1.1.module%2Bel8.8.0%2B21592%2B14a8b93e?epoch=0&upstream=nodejs",
    "nodejs/npm-0:10.2.4-1.18.19.1.1.module%2Bel8.9.0%2B21387%2B21356dec":
        "pkg:rpm/redhat/npm@10.2.4-1.18.19.1.1.module%2Bel8.9.0%2B21387%2B21356dec?epoch=0&upstream=nodejs",
    "nodejs/npm-0:10.2.4-1.18.19.1.1.module%2Bel9.2.0%2B21594%2Ba052107e":
        "pkg:rpm/redhat/npm@10.2.4-1.18.19.1.1.module%2Bel9.2.0%2B21594%2Ba052107e?epoch=0&upstream=nodejs",
    "nodejs/npm-0:10.2.4-1.18.19.1.1.module%2Bel9.3.0%2B21388%2B22892fb9":
        "pkg:rpm/redhat/npm@10.2.4-1.18.19.1.1.module%2Bel9.3.0%2B21388%2B22892fb9?epoch=0&upstream=nodejs",
    "nodejs/npm-0:10.2.4-1.20.11.1.1.module%2Bel8.9.0%2B21380%2B12032667":
        "pkg:rpm/redhat/npm@10.2.4-1.20.11.1.1.module%2Bel8.9.0%2B21380%2B12032667?epoch=0&upstream=nodejs",
    "nodejs/npm-0:10.2.4-1.20.11.1.1.module%2Bel9.3.0%2B21385%2Bbac43d5a":
        "pkg:rpm/redhat/npm@10.2.4-1.20.11.1.1.module%2Bel9.3.0%2B21385%2Bbac43d5a?epoch=0&upstream=nodejs",
    "nodejs/npm-0:8.19.4-1.16.20.2.4.module%2Bel8.6.0%2B21547%2B94389150":
        "pkg:rpm/redhat/npm@8.19.4-1.16.20.2.4.module%2Bel8.6.0%2B21547%2B94389150?epoch=0&upstream=nodejs",
    "nodejs/npm-0:8.19.4-1.16.20.2.4.module%2Bel8.8.0%2B21546%2Becd4bb56":
        "pkg:rpm/redhat/npm@8.19.4-1.16.20.2.4.module%2Bel8.8.0%2B21546%2Becd4bb56?epoch=0&upstream=nodejs",
    "nodejs/npm-1:8.19.4-1.16.20.2.4.el9_0": "pkg:rpm/redhat/npm@8.19.4-1.16.20.2.4.el9_0?epoch=1&upstream=nodejs",
    "nodejs/npm-1:8.19.4-1.16.20.2.4.el9_2": "pkg:rpm/redhat/npm@8.19.4-1.16.20.2.4.el9_2?epoch=1&upstream=nodejs",
    "nodejs/npm-1:8.19.4-1.16.20.2.4.el9_3": "pkg:rpm/redhat/npm@8.19.4-1.16.20.2.4.el9_3?epoch=1&upstream=nodejs",
    "nodejs/v8-12.4-devel": "pkg:rpm/redhat/v8-12.4-devel?upstream=nodejs",
    "nodejs/v8-13.6-devel": "pkg:rpm/redhat/v8-13.6-devel?upstream=nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs": "pkg:rpm/redhat/nodejs?rpmmod=nodejs:16:8090020240315081818:a75119d5",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-0:16.20.2-4.module%2Bel8.9.0%2B21536%2B8fdee1fb":
        "pkg:rpm/redhat/nodejs@16.20.2-4.module%2Bel8.9.0%2B21536%2B8fdee1fb?epoch=0&upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-debuginfo": "pkg:rpm/redhat/nodejs-debuginfo?upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-debugsource":
        "pkg:rpm/redhat/nodejs-debugsource?upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-devel": "pkg:rpm/redhat/nodejs-devel?upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-docs": "pkg:rpm/redhat/nodejs-docs?upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-full-i18n": "pkg:rpm/redhat/nodejs-full-i18n?upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-nodemon-0:3.0.1-1.module%2Bel8.9.0%2B19741%2B03a9aaff":
        "pkg:rpm/redhat/nodejs-nodemon@3.0.1-1.module%2Bel8.9.0%2B19741%2B03a9aaff?epoch=0&upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/nodejs-packaging-0:26-1.module%2Bel8.9.0%2B19858%2Bc237a2cf":
        "pkg:rpm/redhat/nodejs-packaging@26-1.module%2Bel8.9.0%2B19858%2Bc237a2cf?epoch=0&upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:16:8090020240315081818:a75119d5/nodejs/npm-0:8.19.4-1.16.20.2.4.module%2Bel8.9.0%2B21536%2B8fdee1fb":
        "pkg:rpm/redhat/npm@8.19.4-1.16.20.2.4.module%2Bel8.9.0%2B21536%2B8fdee1fb?epoch=0&upstream=nodejs:16:8090020240315081818:a75119d5/nodejs",
    "nodejs:18:8090020240301110609:a75119d5/nodejs": "pkg:rpm/redhat/nodejs?rpmmod=nodejs:18:8090020240301110609:a75119d5",
    "nodejs:18:9030020240301111035:rhel9/nodejs": "pkg:rpm/redhat/nodejs?rpmmod=nodejs:18:9030020240301111035:rhel9",
    "nodejs:20:8090020240228165436:a75119d5/nodejs": "pkg:rpm/redhat/nodejs?rpmmod=nodejs:20:8090020240228165436:a75119d5",
    "nodejs:20:9030020240229115828:rhel9/nodejs": "pkg:rpm/redhat/nodejs?rpmmod=nodejs:20:9030020240229115828:rhel9",
    "odf4/mcg-core-rhel8": "pkg:oci/mcg-core-rhel8?repository_url=registry.redhat.io/odf4/mcg-core-rhel8",
    "rh-nodejs14-nodejs-0:14.21.3-6.el7.src": "pkg:rpm/redhat/rh-nodejs14-nodejs@14.21.3-6.el7?arch=src&epoch=0",
    "rh-nodejs14-nodejs/rh-nodejs14-nodejs-0:14.21.3-6.el7": "pkg:rpm/redhat/rh-nodejs14-nodejs@14.21.3-6.el7?epoch=0&upstream=rh-nodejs14-nodejs",
    "rh-nodejs14-nodejs/rh-nodejs14-nodejs-debuginfo": "pkg:rpm/redhat/rh-nodejs14-nodejs-debuginfo?upstream=rh-nodejs14-nodejs",
    "rh-nodejs14-nodejs/rh-nodejs14-nodejs-devel": "pkg:rpm/redhat/rh-nodejs14-nodejs-devel?upstream=rh-nodejs14-nodejs",
    "rh-nodejs14-nodejs/rh-nodejs14-nodejs-docs": "pkg:rpm/redhat/rh-nodejs14-nodejs-docs?upstream=rh-nodejs14-nodejs",
    "rh-nodejs14-nodejs/rh-nodejs14-nodejs-full-i18n": "pkg:rpm/redhat/rh-nodejs14-nodejs-full-i18n?upstream=rh-nodejs14-nodejs",
    "rh-nodejs14-nodejs/rh-nodejs14-npm-0:6.14.18-14.21.3.6.el7": "pkg:rpm/redhat/rh-nodejs14-npm@6.14.18-14.21.3.6.el7?epoch=0&upstream=rh-nodejs14-nodejs",
    "vim.src": "pkg:rpm/redhat/vim?arch=src",
    "vim/vim": "pkg:rpm/redhat/vim?upstream=vim",
    "vim/vim-common": "pkg:rpm/redhat/vim-common?upstream=vim",
    "vim/vim-common-debuginfo": "pkg:rpm/redhat/vim-common-debuginfo?upstream=vim",
    "vim/vim-debuginfo": "pkg:rpm/redhat/vim-debuginfo?upstream=vim",
    "vim/vim-debugsource": "pkg:rpm/redhat/vim-debugsource?upstream=vim",
    "vim/vim-enhanced": "pkg:rpm/redhat/vim-enhanced?upstream=vim",
    "vim/vim-enhanced-debuginfo": "pkg:rpm/redhat/vim-enhanced-debuginfo?upstream=vim",
    "vim/vim-filesystem": "pkg:rpm/redhat/vim-filesystem?upstream=vim",
    "vim/vim-minimal": "pkg:rpm/redhat/vim-minimal?upstream=vim",
    "vim/vim-minimal-debuginfo": "pkg:rpm/redhat/vim-minimal-debuginfo?upstream=vim",
    "vim/vim-X11": "pkg:rpm/redhat/vim-X11?upstream=vim",
    "vim/vim-X11-debuginfo": "pkg:rpm/redhat/vim-X11-debuginfo?upstream=vim",
    "aardvark-dns-0:1.5.0-2.module+el8.8.0+21265+93802b02.src": "pkg:rpm/redhat/aardvark-dns@1.5.0-2.module%2Bel8.8.0%2B21265%2B93802b02?arch=src&epoch=0",
    "aardvark-dns-0:1.7.0-1.module+el8.9.0+21243+a586538b.src": "pkg:rpm/redhat/aardvark-dns@1.7.0-1.module%2Bel8.9.0%2B21243%2Ba586538b?arch=src&epoch=0",
    "aardvark-dns/aardvark-dns": "pkg:rpm/redhat/aardvark-dns?upstream=aardvark-dns",
    "buildah-0:1.11.6-8.module+el8.2.0+21264+96602818.src": "pkg:rpm/redhat/buildah@1.11.6-8.module%2Bel8.2.0%2B21264%2B96602818?arch=src&epoch=0",
    "buildah-0:1.19.9-1.module+el8.4.0+21078+a96cfbf6.src": "pkg:rpm/redhat/buildah@1.19.9-1.module%2Bel8.4.0%2B21078%2Ba96cfbf6?arch=src&epoch=0",
    "buildah-0:1.24.2-3.module+el8.6.0+21254+7ef668f8.src": "pkg:rpm/redhat/buildah@1.24.2-3.module%2Bel8.6.0%2B21254%2B7ef668f8?arch=src&epoch=0",
    "buildah-0:1.24.6-7.module+el8.9.0+21242+944321bb.src": "pkg:rpm/redhat/buildah@1.24.6-7.module%2Bel8.9.0%2B21242%2B944321bb?arch=src&epoch=0",
    "buildah-0:1.26.2-1.module+el8.6.0+21266+3e24c7b3.src": "pkg:rpm/redhat/buildah@1.26.2-1.module%2Bel8.6.0%2B21266%2B3e24c7b3?arch=src&epoch=0",
    "buildah.src": "pkg:rpm/redhat/buildah?arch=src",
    "buildah/buildah": "pkg:rpm/redhat/buildah?upstream=buildah",
    "buildah/buildah-debuginfo": "pkg:rpm/redhat/buildah-debuginfo?upstream=buildah",
    "buildah/buildah-debugsource": "pkg:rpm/redhat/buildah-debugsource?upstream=buildah",
    "buildah/buildah-tests": "pkg:rpm/redhat/buildah-tests?upstream=buildah",
    "buildah/buildah-tests-debuginfo": "pkg:rpm/redhat/buildah-tests-debuginfo?upstream=buildah",
    "container-native-virtualization/passt-network-binding-plugin-cni-rhel9": (
        "pkg:oci/passt-network-binding-plugin-cni-rhel9"
        "?repository_url=registry.redhat.io/container-native-virtualization/passt-network-binding-plugin-cni-rhel9"
    ),
    "container-native-virtualization/passt-network-binding-plugin-sidecar-rhel9": (
        "pkg:oci/passt-network-binding-plugin-sidecar-rhel9"
        "?repository_url=registry.redhat.io/container-native-virtualization/passt-network-binding-plugin-sidecar-rhel9"
    ),
    "container-native-virtualization/sidecar-shim-rhel9":
        "pkg:oci/sidecar-shim-rhel9?repository_url=registry.redhat.io/container-native-virtualization/sidecar-shim-rhel9",
    "container-native-virtualization/virt-api": "pkg:oci/virt-api?repository_url=registry.redhat.io/container-native-virtualization/virt-api",
    "container-native-virtualization/virt-api-rhel9": "pkg:oci/virt-api-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-api-rhel9",
    "container-native-virtualization/virt-artifacts-server":
        "pkg:oci/virt-artifacts-server?repository_url=registry.redhat.io/container-native-virtualization/virt-artifacts-server",
    "container-native-virtualization/virt-artifacts-server-rhel9":
        "pkg:oci/virt-artifacts-server-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-artifacts-server-rhel9",
    "container-native-virtualization/virt-controller":
        "pkg:oci/virt-controller?repository_url=registry.redhat.io/container-native-virtualization/virt-controller",
    "container-native-virtualization/virt-controller-rhel9":
        "pkg:oci/virt-controller-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-controller-rhel9",
    "container-native-virtualization/virt-exportproxy":
        "pkg:oci/virt-exportproxy?repository_url=registry.redhat.io/container-native-virtualization/virt-exportproxy",
    "container-native-virtualization/virt-exportproxy-rhel9":
        "pkg:oci/virt-exportproxy-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-exportproxy-rhel9",
    "container-native-virtualization/virt-exportserver":
        "pkg:oci/virt-exportserver?repository_url=registry.redhat.io/container-native-virtualization/virt-exportserver",
    "container-native-virtualization/virt-exportserver-rhel9":
        "pkg:oci/virt-exportserver-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-exportserver-rhel9",
    "container-native-virtualization/virt-handler": "pkg:oci/virt-handler?repository_url=registry.redhat.io/container-native-virtualization/virt-handler",
    "container-native-virtualization/virt-handler-rhel9":
        "pkg:oci/virt-handler-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-handler-rhel9",
    "container-native-virtualization/virt-launcher": "pkg:oci/virt-launcher?repository_url=registry.redhat.io/container-native-virtualization/virt-launcher",
    "container-native-virtualization/virt-launcher-rhel9":
        "pkg:oci/virt-launcher-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-launcher-rhel9",
    "container-native-virtualization/virt-operator": "pkg:oci/virt-operator?repository_url=registry.redhat.io/container-native-virtualization/virt-operator",
    "container-native-virtualization/virt-operator-rhel9":
        "pkg:oci/virt-operator-rhel9?repository_url=registry.redhat.io/container-native-virtualization/virt-operator-rhel9",
    "container-native-virtualization/wasp-agent-rhel9":
        "pkg:oci/wasp-agent-rhel9?repository_url=registry.redhat.io/container-native-virtualization/wasp-agent-rhel9",
    "container-tools:4.0/runc.src": "pkg:rpm/redhat/runc?arch=src&rpmmod=container-tools:4.0",
    "container-tools:4.0/runc/runc": "pkg:rpm/redhat/runc?upstream=container-tools:4.0/runc",
    "container-tools:4.0/runc/runc-debuginfo": "pkg:rpm/redhat/runc-debuginfo?upstream=container-tools:4.0/runc",
    "container-tools:4.0/runc/runc-debugsource": "pkg:rpm/redhat/runc-debugsource?upstream=container-tools:4.0/runc",
    "container-tools:rhel8/buildah.src": "pkg:rpm/redhat/buildah?arch=src&rpmmod=container-tools:rhel8",
    "container-tools:rhel8/buildah/buildah": "pkg:rpm/redhat/buildah?upstream=container-tools:rhel8/buildah",
    "container-tools:rhel8/buildah/buildah-debuginfo": "pkg:rpm/redhat/buildah-debuginfo?upstream=container-tools:rhel8/buildah",
    "container-tools:rhel8/buildah/buildah-debugsource": "pkg:rpm/redhat/buildah-debugsource?upstream=container-tools:rhel8/buildah",
    "container-tools:rhel8/buildah/buildah-tests": "pkg:rpm/redhat/buildah-tests?upstream=container-tools:rhel8/buildah",
    "container-tools:rhel8/buildah/buildah-tests-debuginfo": "pkg:rpm/redhat/buildah-tests-debuginfo?upstream=container-tools:rhel8/buildah",
    "container-tools:rhel8/podman.src": "pkg:rpm/redhat/podman?arch=src&rpmmod=container-tools:rhel8",
    "container-tools:rhel8/podman/containernetworking-plugins": "pkg:rpm/redhat/containernetworking-plugins?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman": "pkg:rpm/redhat/podman?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-catatonit": "pkg:rpm/redhat/podman-catatonit?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-catatonit-debuginfo": "pkg:rpm/redhat/podman-catatonit-debuginfo?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-debuginfo": "pkg:rpm/redhat/podman-debuginfo?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-debugsource": "pkg:rpm/redhat/podman-debugsource?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-docker": "pkg:rpm/redhat/podman-docker?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-gvproxy": "pkg:rpm/redhat/podman-gvproxy?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-gvproxy-debuginfo": "pkg:rpm/redhat/podman-gvproxy-debuginfo?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-manpages": "pkg:rpm/redhat/podman-manpages?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-plugins": "pkg:rpm/redhat/podman-plugins?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-plugins-debuginfo": "pkg:rpm/redhat/podman-plugins-debuginfo?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-remote": "pkg:rpm/redhat/podman-remote?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-remote-debuginfo": "pkg:rpm/redhat/podman-remote-debuginfo?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/podman/podman-tests": "pkg:rpm/redhat/podman-tests?upstream=container-tools:rhel8/podman",
    "container-tools:rhel8/runc.src": "pkg:rpm/redhat/runc?arch=src&rpmmod=container-tools:rhel8",
    "container-tools:rhel8/runc/runc": "pkg:rpm/redhat/runc?upstream=container-tools:rhel8/runc",
    "container-tools:rhel8/runc/runc-debuginfo": "pkg:rpm/redhat/runc-debuginfo?upstream=container-tools:rhel8/runc",
    "container-tools:rhel8/runc/runc-debugsource": "pkg:rpm/redhat/runc-debugsource?upstream=container-tools:rhel8/runc",
    "containers-common.src": "pkg:rpm/redhat/containers-common?arch=src",
    "containers-common/aardvark-dns": "pkg:rpm/redhat/aardvark-dns?upstream=containers-common",
    "containers-common/containers-common": "pkg:rpm/redhat/containers-common?upstream=containers-common",
    "containers-common/containers-common-extra": "pkg:rpm/redhat/containers-common-extra?upstream=containers-common",
    "containers-common/netavark": "pkg:rpm/redhat/netavark?upstream=containers-common",
    "cri-o.src": "pkg:rpm/redhat/cri-o?arch=src",
    "cri-o/cri-o": "pkg:rpm/redhat/cri-o?upstream=cri-o",
    "cri-o/cri-o-debuginfo": "pkg:rpm/redhat/cri-o-debuginfo?upstream=cri-o",
    "cri-o/cri-o-debugsource": "pkg:rpm/redhat/cri-o-debugsource?upstream=cri-o",
    "cri-tools.src": "pkg:rpm/redhat/cri-tools?arch=src",
    "cri-tools/cri-tools": "pkg:rpm/redhat/cri-tools?upstream=cri-tools",
    "cri-tools/cri-tools-debuginfo": "pkg:rpm/redhat/cri-tools-debuginfo?upstream=cri-tools",
    "cri-tools/cri-tools-debugsource": "pkg:rpm/redhat/cri-tools-debugsource?upstream=cri-tools",
    "docker-2:1.13.1-210.git7d71120.el7_9.src": "pkg:rpm/redhat/docker@1.13.1-210.git7d71120.el7_9?arch=src&epoch=2",
    "docker/atomic": "pkg:rpm/redhat/atomic?upstream=docker",
    "docker/container-selinux": "pkg:rpm/redhat/container-selinux?upstream=docker",
    "docker/docker-2:1.13.1-210.git7d71120.el7_9": "pkg:rpm/redhat/docker@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/docker-client-2:1.13.1-210.git7d71120.el7_9": "pkg:rpm/redhat/docker-client@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/docker-common-2:1.13.1-210.git7d71120.el7_9": "pkg:rpm/redhat/docker-common@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/docker-debuginfo": "pkg:rpm/redhat/docker-debuginfo?upstream=docker",
    "docker/docker-forward-journald": "pkg:rpm/redhat/docker-forward-journald?upstream=docker",
    "docker/docker-logrotate-2:1.13.1-210.git7d71120.el7_9": "pkg:rpm/redhat/docker-logrotate@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/docker-lvm-plugin-2:1.13.1-210.git7d71120.el7_9": "pkg:rpm/redhat/docker-lvm-plugin@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/docker-novolume-plugin-2:1.13.1-210.git7d71120.el7_9": "pkg:rpm/redhat/docker-novolume-plugin@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/docker-python": "pkg:rpm/redhat/docker-python?upstream=docker",
    "docker/docker-rhel-push-plugin-2:1.13.1-210.git7d71120.el7_9":
        "pkg:rpm/redhat/docker-rhel-push-plugin@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/docker-selinux": "pkg:rpm/redhat/docker-selinux?upstream=docker",
    "docker/docker-unit-test": "pkg:rpm/redhat/docker-unit-test?upstream=docker",
    "docker/docker-v1.10-migrator-2:1.13.1-210.git7d71120.el7_9": "pkg:rpm/redhat/docker-v1.10-migrator@1.13.1-210.git7d71120.el7_9?epoch=2&upstream=docker",
    "docker/oci-register-machine": "pkg:rpm/redhat/oci-register-machine?upstream=docker",
    "docker/oci-systemd-hook": "pkg:rpm/redhat/oci-systemd-hook?upstream=docker",
    "docker/oci-umount": "pkg:rpm/redhat/oci-umount?upstream=docker",
    "docker/python-websocket-client": "pkg:rpm/redhat/python-websocket-client?upstream=docker",
    "jenkins-0:2-plugins-4.15.1718879538-1.el8.src": "pkg:rpm/redhat/jenkins@2-plugins-4.15.1718879538-1.el8?arch=src&epoch=0",
    "jenkins/jenkins-0:2.440.3.1718879390-3.el8": "pkg:rpm/redhat/jenkins@2.440.3.1718879390-3.el8?epoch=0&upstream=jenkins",
    "jenkins/jenkins-2-plugins-0:4.15.1718879538-1.el8": "pkg:rpm/redhat/jenkins-2-plugins@4.15.1718879538-1.el8?epoch=0&upstream=jenkins",
    "kepler-container": "pkg:oci/kepler-container?repository_url=registry.redhat.io/kepler-container",
    "kubevirt.src": "pkg:rpm/redhat/kubevirt?arch=src",
    "kubevirt/kubevirt": "pkg:rpm/redhat/kubevirt?upstream=kubevirt",
    "kubevirt/kubevirt-virtctl": "pkg:rpm/redhat/kubevirt-virtctl?upstream=kubevirt",
    "kubevirt/kubevirt-virtctl-redistributable": "pkg:rpm/redhat/kubevirt-virtctl-redistributable?upstream=kubevirt",
    "microshift-0:4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9.src":
        "pkg:rpm/redhat/microshift@4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9?arch=src&epoch=0",
    "microshift-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9.src":
        "pkg:rpm/redhat/microshift@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?arch=src&epoch=0",
    "microshift-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9.src":
        "pkg:rpm/redhat/microshift@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?arch=src&epoch=0",
    "microshift-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9.src":
        "pkg:rpm/redhat/microshift@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?arch=src&epoch=0",
    "microshift.src": "pkg:rpm/redhat/microshift?arch=src",
    "microshift/microshift": "pkg:rpm/redhat/microshift?upstream=microshift",
    "microshift/microshift-0:4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9":
        "pkg:rpm/redhat/microshift@4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9?epoch=0&upstream=microshift",
    "microshift/microshift-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9":
        "pkg:rpm/redhat/microshift@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?epoch=0&upstream=microshift",
    "microshift/microshift-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-gateway-api": "pkg:rpm/redhat/microshift-gateway-api?upstream=microshift",
    "microshift/microshift-gateway-api-release-info": "pkg:rpm/redhat/microshift-gateway-api-release-info?upstream=microshift",
    "microshift/microshift-greenboot": "pkg:rpm/redhat/microshift-greenboot?upstream=microshift",
    "microshift/microshift-greenboot-0:4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9":
        "pkg:rpm/redhat/microshift-greenboot@4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9?epoch=0&upstream=microshift",
    "microshift/microshift-greenboot-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9":
        "pkg:rpm/redhat/microshift-greenboot@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?epoch=0&upstream=microshift",
    "microshift/microshift-greenboot-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-greenboot@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-greenboot-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-greenboot@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-low-latency": "pkg:rpm/redhat/microshift-low-latency?upstream=microshift",
    "microshift/microshift-low-latency-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-low-latency@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-multus": "pkg:rpm/redhat/microshift-multus?upstream=microshift",
    "microshift/microshift-multus-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-multus@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-multus-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-multus@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-multus-release-info": "pkg:rpm/redhat/microshift-multus-release-info?upstream=microshift",
    "microshift/microshift-multus-release-info-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-multus-release-info@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-multus-release-info-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-multus-release-info@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-networking": "pkg:rpm/redhat/microshift-networking?upstream=microshift",
    "microshift/microshift-networking-0:4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9":
        "pkg:rpm/redhat/microshift-networking@4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9?epoch=0&upstream=microshift",
    "microshift/microshift-networking-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9":
        "pkg:rpm/redhat/microshift-networking@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?epoch=0&upstream=microshift",
    "microshift/microshift-networking-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-networking@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-networking-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-networking@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-olm": "pkg:rpm/redhat/microshift-olm?upstream=microshift",
    "microshift/microshift-olm-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9":
        "pkg:rpm/redhat/microshift-olm@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?epoch=0&upstream=microshift",
    "microshift/microshift-olm-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-olm@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-olm-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-olm@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-olm-release-info": "pkg:rpm/redhat/microshift-olm-release-info?upstream=microshift",
    "microshift/microshift-olm-release-info-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9":
        "pkg:rpm/redhat/microshift-olm-release-info@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?epoch=0&upstream=microshift",
    "microshift/microshift-olm-release-info-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-olm-release-info@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-olm-release-info-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-olm-release-info@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-release-info": "pkg:rpm/redhat/microshift-release-info?upstream=microshift",
    "microshift/microshift-release-info-0:4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9":
        "pkg:rpm/redhat/microshift-release-info@4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9?epoch=0&upstream=microshift",
    "microshift/microshift-release-info-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9":
        "pkg:rpm/redhat/microshift-release-info@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?epoch=0&upstream=microshift",
    "microshift/microshift-release-info-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-release-info@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-release-info-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-release-info@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "microshift/microshift-selinux": "pkg:rpm/redhat/microshift-selinux?upstream=microshift",
    "microshift/microshift-selinux-0:4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9":
        "pkg:rpm/redhat/microshift-selinux@4.14.42-202411280904.p0.gcf4d04f.assembly.4.14.42.el9?epoch=0&upstream=microshift",
    "microshift/microshift-selinux-0:4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9":
        "pkg:rpm/redhat/microshift-selinux@4.15.41-202412091343.p0.gcf9680e.assembly.4.15.41.el9?epoch=0&upstream=microshift",
    "microshift/microshift-selinux-0:4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9":
        "pkg:rpm/redhat/microshift-selinux@4.16.24-202411220522.p0.gcc4fedc.assembly.4.16.24.el9?epoch=0&upstream=microshift",
    "microshift/microshift-selinux-0:4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9":
        "pkg:rpm/redhat/microshift-selinux@4.17.7-202411280904.p0.g129334d.assembly.4.17.7.el9?epoch=0&upstream=microshift",
    "ocp-tools-4/jenkins-agent-base-rhel8": "pkg:oci/jenkins-agent-base-rhel8?repository_url=registry.redhat.io/ocp-tools-4/jenkins-agent-base-rhel8",
    "ocp-tools-4/jenkins-rhel8": "pkg:oci/jenkins-rhel8?repository_url=registry.redhat.io/ocp-tools-4/jenkins-rhel8",
    "openshift-enterprise-builder-container-v4.17.0-0:202501052337.p0.gbb33e13.assembly.stream.el9":
        "pkg:rpm/redhat/openshift-enterprise-builder-container-v4.17.0@202501052337.p0.gbb33e13.assembly.stream.el9?epoch=0",
    "openshift.src": "pkg:rpm/redhat/openshift?arch=src",
    "openshift/openshift": "pkg:rpm/redhat/openshift?upstream=openshift",
    "openshift/openshift-clients": "pkg:rpm/redhat/openshift-clients?upstream=openshift",
    "openshift/openshift-clients-redistributable": "pkg:rpm/redhat/openshift-clients-redistributable?upstream=openshift",
    "openshift/openshift-hyperkube": "pkg:rpm/redhat/openshift-hyperkube?upstream=openshift",
    "openshift4/ose-aws-ebs-csi-driver-rhel9": "pkg:oci/ose-aws-ebs-csi-driver-rhel9?repository_url=registry.redhat.io/openshift4/ose-aws-ebs-csi-driver-rhel9",
    "openshift4/ose-aws-efs-csi-driver-container-rhel8":
        "pkg:oci/ose-aws-efs-csi-driver-container-rhel8?repository_url=registry.redhat.io/openshift4/ose-aws-efs-csi-driver-container-rhel8",
    "openshift4/ose-csi-driver-nfs-rhel8": "pkg:oci/ose-csi-driver-nfs-rhel8?repository_url=registry.redhat.io/openshift4/ose-csi-driver-nfs-rhel8",
    "openshift4/ose-docker-builder-rhel9": "pkg:oci/ose-docker-builder-rhel9?repository_url=registry.redhat.io/openshift4/ose-docker-builder-rhel9",
    "openshift4/ose-docker-builder-rhel9-0:202501160405.p0.g300d9ad.assembly.stream.el9":
        "pkg:oci/ose-docker-builder-rhel9@202501160405.p0.g300d9ad.assembly.stream.el9?repository_url=registry.redhat.io/openshift4/ose-docker-builder-rhel9",
    "openshift4/ose-docker-builder-rhel9-0:202502171304.p0.gb74eb6d.assembly.stream.el8":
        "pkg:oci/ose-docker-builder-rhel9@202502171304.p0.gb74eb6d.assembly.stream.el8?repository_url=registry.redhat.io/openshift4/ose-docker-builder-rhel9",
    "openshift4/ose-docker-builder-rhel9-0:202503030130.p0.g7c2a284.assembly.stream.el8":
        "pkg:oci/ose-docker-builder-rhel9@202503030130.p0.g7c2a284.assembly.stream.el8?repository_url=registry.redhat.io/openshift4/ose-docker-builder-rhel9",
    "openshift4/ose-docker-builder-rhel9-0:202503060906.p0.gb03f3f5.assembly.stream.el8":
        "pkg:oci/ose-docker-builder-rhel9@202503060906.p0.gb03f3f5.assembly.stream.el8?repository_url=registry.redhat.io/openshift4/ose-docker-builder-rhel9",
    "openshift4/ose-docker-builder-rhel9-0:202503111300.p0.gb379980.assembly.stream.el8":
        "pkg:oci/ose-docker-builder-rhel9@202503111300.p0.gb379980.assembly.stream.el8?repository_url=registry.redhat.io/openshift4/ose-docker-builder-rhel9",
    "openshift4/ose-hyperkube-rhel9": "pkg:oci/ose-hyperkube-rhel9?repository_url=registry.redhat.io/openshift4/ose-hyperkube-rhel9",
    "openshift4/ose-kube-proxy": "pkg:oci/ose-kube-proxy?repository_url=registry.redhat.io/openshift4/ose-kube-proxy",
    "openshift4/ose-node-feature-discovery": "pkg:oci/ose-node-feature-discovery?repository_url=registry.redhat.io/openshift4/ose-node-feature-discovery",
    "openshift4/ose-powervs-block-csi-driver-rhel8":
        "pkg:oci/ose-powervs-block-csi-driver-rhel8?repository_url=registry.redhat.io/openshift4/ose-powervs-block-csi-driver-rhel8",
    "openshift4/ose-sdn-rhel8": "pkg:oci/ose-sdn-rhel8?repository_url=registry.redhat.io/openshift4/ose-sdn-rhel8",
    "openshift4/ose-tests": "pkg:oci/ose-tests?repository_url=registry.redhat.io/openshift4/ose-tests",
    "openshift4/ose-vsphere-csi-driver-rhel8": "pkg:oci/ose-vsphere-csi-driver-rhel8?repository_url=registry.redhat.io/openshift4/ose-vsphere-csi-driver-rhel8",
    "openshift4/ose-vsphere-csi-driver-syncer-rhel8":
        "pkg:oci/ose-vsphere-csi-driver-syncer-rhel8?repository_url=registry.redhat.io/openshift4/ose-vsphere-csi-driver-syncer-rhel8",
    "podman.src": "pkg:rpm/redhat/podman?arch=src",
    "podman/containernetworking-plugins": "pkg:rpm/redhat/containernetworking-plugins?upstream=podman",
    "podman/podman": "pkg:rpm/redhat/podman?upstream=podman",
    "podman/podman-catatonit": "pkg:rpm/redhat/podman-catatonit?upstream=podman",
    "podman/podman-catatonit-debuginfo": "pkg:rpm/redhat/podman-catatonit-debuginfo?upstream=podman",
    "podman/podman-debuginfo": "pkg:rpm/redhat/podman-debuginfo?upstream=podman",
    "podman/podman-debugsource": "pkg:rpm/redhat/podman-debugsource?upstream=podman",
    "podman/podman-docker": "pkg:rpm/redhat/podman-docker?upstream=podman",
    "podman/podman-gvproxy": "pkg:rpm/redhat/podman-gvproxy?upstream=podman",
    "podman/podman-gvproxy-debuginfo": "pkg:rpm/redhat/podman-gvproxy-debuginfo?upstream=podman",
    "podman/podman-machine": "pkg:rpm/redhat/podman-machine?upstream=podman",
    "podman/podman-plugins": "pkg:rpm/redhat/podman-plugins?upstream=podman",
    "podman/podman-plugins-debuginfo": "pkg:rpm/redhat/podman-plugins-debuginfo?upstream=podman",
    "podman/podman-remote": "pkg:rpm/redhat/podman-remote?upstream=podman",
    "podman/podman-remote-debuginfo": "pkg:rpm/redhat/podman-remote-debuginfo?upstream=podman",
    "podman/podman-tests": "pkg:rpm/redhat/podman-tests?upstream=podman",
    "podman/podman-tests-debuginfo": "pkg:rpm/redhat/podman-tests-debuginfo?upstream=podman",
    "podman/podmansh": "pkg:rpm/redhat/podmansh?upstream=podman",
    "quay/quay-builder-rhel8": "pkg:oci/quay-builder-rhel8?repository_url=registry.redhat.io/quay/quay-builder-rhel8",
    "runc-0:1.0.0-70.rc10.el7_9.src": "pkg:rpm/redhat/runc@1.0.0-70.rc10.el7_9?arch=src&epoch=0",
    "runc-3:1.1.2-3.1.rhaos4.11.el8.src": "pkg:rpm/redhat/runc@1.1.2-3.1.rhaos4.11.el8?arch=src&epoch=3",
    "runc-3:1.1.6-5.1.rhaos4.12.el8.src": "pkg:rpm/redhat/runc@1.1.6-5.1.rhaos4.12.el8?arch=src&epoch=3",
    "runc-4:1.1.12-1.el9_0.src": "pkg:rpm/redhat/runc@1.1.12-1.el9_0?arch=src&epoch=4",
    "runc-4:1.1.12-1.el9_2.src": "pkg:rpm/redhat/runc@1.1.12-1.el9_2?arch=src&epoch=4",
    "runc-4:1.1.12-1.el9_3.src": "pkg:rpm/redhat/runc@1.1.12-1.el9_3?arch=src&epoch=4",
    "runc-4:1.1.12-1.rhaos4.13.el8.src": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.13.el8?arch=src&epoch=4",
    "runc-4:1.1.12-1.rhaos4.13.el9.src": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.13.el9?arch=src&epoch=4",
    "runc-4:1.1.12-1.rhaos4.14.el8.src": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.14.el8?arch=src&epoch=4",
    "runc-4:1.1.12-1.rhaos4.14.el9.src": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.14.el9?arch=src&epoch=4",
    "runc.src": "pkg:rpm/redhat/runc?arch=src",
    "runc/runc": "pkg:rpm/redhat/runc?upstream=runc",
    "runc/runc-0:1.0.0-70.rc10.el7_9": "pkg:rpm/redhat/runc@1.0.0-70.rc10.el7_9?epoch=0&upstream=runc",
    "runc/runc-3:1.1.2-3.1.rhaos4.11.el8": "pkg:rpm/redhat/runc@1.1.2-3.1.rhaos4.11.el8?epoch=3&upstream=runc",
    "runc/runc-3:1.1.6-5.1.rhaos4.12.el8": "pkg:rpm/redhat/runc@1.1.6-5.1.rhaos4.12.el8?epoch=3&upstream=runc",
    "runc/runc-4:1.1.12-1.el9_0": "pkg:rpm/redhat/runc@1.1.12-1.el9_0?epoch=4&upstream=runc",
    "runc/runc-4:1.1.12-1.el9_2": "pkg:rpm/redhat/runc@1.1.12-1.el9_2?epoch=4&upstream=runc",
    "runc/runc-4:1.1.12-1.el9_3": "pkg:rpm/redhat/runc@1.1.12-1.el9_3?epoch=4&upstream=runc",
    "runc/runc-4:1.1.12-1.rhaos4.13.el8": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.13.el8?epoch=4&upstream=runc",
    "runc/runc-4:1.1.12-1.rhaos4.13.el9": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.13.el9?epoch=4&upstream=runc",
    "runc/runc-4:1.1.12-1.rhaos4.14.el8": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.14.el8?epoch=4&upstream=runc",
    "runc/runc-4:1.1.12-1.rhaos4.14.el9": "pkg:rpm/redhat/runc@1.1.12-1.rhaos4.14.el9?epoch=4&upstream=runc",
    "runc/runc-debuginfo": "pkg:rpm/redhat/runc-debuginfo?upstream=runc",
    "runc/runc-debugsource": "pkg:rpm/redhat/runc-debugsource?upstream=runc",
    "cluster-logging-operator-container-v5.8.6-0:11": "pkg:rpm/redhat/cluster-logging-operator-container-v5.8.6@11?epoch=0",
    "cluster-logging-operator-metadata-container-v5.8.6-0:22": "pkg:rpm/redhat/cluster-logging-operator-metadata-container-v5.8.6@22?epoch=0",
    "elasticsearch-operator-container-v5.8.6-0:7": "pkg:rpm/redhat/elasticsearch-operator-container-v5.8.6@7?epoch=0",
    "elasticsearch-operator-metadata-container-v5.8.6-0:19": "pkg:rpm/redhat/elasticsearch-operator-metadata-container-v5.8.6@19?epoch=0",
    "elasticsearch-proxy-container-v1.0.0-0:479": "pkg:rpm/redhat/elasticsearch-proxy-container-v1.0.0@479?epoch=0",
    "kernel-0:4.18.0-193.128.1.el8_2.src": "pkg:rpm/redhat/kernel@4.18.0-193.128.1.el8_2?arch=src&epoch=0",
    "kernel-0:4.18.0-305.125.1.el8_4.src": "pkg:rpm/redhat/kernel@4.18.0-305.125.1.el8_4?arch=src&epoch=0",
    "kernel-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel@4.18.0-372.91.1.el8_6?epoch=0",
    "kernel-0:4.18.0-372.91.1.el8_6.src": "pkg:rpm/redhat/kernel@4.18.0-372.91.1.el8_6?arch=src&epoch=0",
    "kernel-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel@4.18.0-477.51.1.el8_8?epoch=0",
    "kernel-0:4.18.0-477.51.1.el8_8.src": "pkg:rpm/redhat/kernel@4.18.0-477.51.1.el8_8?arch=src&epoch=0",
    "kernel-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel@4.18.0-513.18.1.el8_9?epoch=0",
    "kernel-0:4.18.0-513.18.1.el8_9.src": "pkg:rpm/redhat/kernel@4.18.0-513.18.1.el8_9?arch=src&epoch=0",
    "kernel-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel@5.14.0-284.52.1.el9_2?epoch=0",
    "kernel-0:5.14.0-284.52.1.el9_2.src": "pkg:rpm/redhat/kernel@5.14.0-284.52.1.el9_2?arch=src&epoch=0",
    "kernel-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel@5.14.0-362.24.1.el9_3?epoch=0",
    "kernel-0:5.14.0-362.24.1.el9_3.src": "pkg:rpm/redhat/kernel@5.14.0-362.24.1.el9_3?arch=src&epoch=0",
    "kernel-0:5.14.0-70.93.2.el9_0.src": "pkg:rpm/redhat/kernel@5.14.0-70.93.2.el9_0?arch=src&epoch=0",
    "kernel-rt-0:4.18.0-193.128.1.rt13.179.el8_2.src": "pkg:rpm/redhat/kernel-rt@4.18.0-193.128.1.rt13.179.el8_2?arch=src&epoch=0",
    "kernel-rt-0:4.18.0-305.125.1.rt7.201.el8_4.src": "pkg:rpm/redhat/kernel-rt@4.18.0-305.125.1.rt7.201.el8_4?arch=src&epoch=0",
    "kernel-rt-0:4.18.0-513.18.1.rt7.320.el8_9.src": "pkg:rpm/redhat/kernel-rt@4.18.0-513.18.1.rt7.320.el8_9?arch=src&epoch=0",
    "kernel-rt-0:5.14.0-284.52.1.rt14.337.el9_2.src": "pkg:rpm/redhat/kernel-rt@5.14.0-284.52.1.rt14.337.el9_2?arch=src&epoch=0",
    "kernel-rt-0:5.14.0-70.93.1.rt21.165.el9_0.src": "pkg:rpm/redhat/kernel-rt@5.14.0-70.93.1.rt21.165.el9_0?arch=src&epoch=0",
    "kernel-rt.src": "pkg:rpm/redhat/kernel-rt?arch=src",
    "kernel-rt/kernel-rt": "pkg:rpm/redhat/kernel-rt?upstream=kernel-rt",
    "kernel-rt/kernel-rt-0:4.18.0-193.128.1.rt13.179.el8_2": "pkg:rpm/redhat/kernel-rt@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-0:4.18.0-305.125.1.rt7.201.el8_4": "pkg:rpm/redhat/kernel-rt@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-0:4.18.0-513.18.1.rt7.320.el8_9": "pkg:rpm/redhat/kernel-rt@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-0:5.14.0-284.52.1.rt14.337.el9_2": "pkg:rpm/redhat/kernel-rt@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-0:5.14.0-70.93.1.rt21.165.el9_0": "pkg:rpm/redhat/kernel-rt@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-core": "pkg:rpm/redhat/kernel-rt-core?upstream=kernel-rt",
    "kernel-rt/kernel-rt-core-0:4.18.0-193.128.1.rt13.179.el8_2": "pkg:rpm/redhat/kernel-rt-core@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-core-0:4.18.0-305.125.1.rt7.201.el8_4": "pkg:rpm/redhat/kernel-rt-core@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-core-0:4.18.0-513.18.1.rt7.320.el8_9": "pkg:rpm/redhat/kernel-rt-core@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-core-0:5.14.0-284.52.1.rt14.337.el9_2": "pkg:rpm/redhat/kernel-rt-core@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-core-0:5.14.0-70.93.1.rt21.165.el9_0": "pkg:rpm/redhat/kernel-rt-core@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug": "pkg:rpm/redhat/kernel-rt-debug?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-0:4.18.0-193.128.1.rt13.179.el8_2": "pkg:rpm/redhat/kernel-rt-debug@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-0:4.18.0-305.125.1.rt7.201.el8_4": "pkg:rpm/redhat/kernel-rt-debug@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-0:4.18.0-513.18.1.rt7.320.el8_9": "pkg:rpm/redhat/kernel-rt-debug@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-0:5.14.0-284.52.1.rt14.337.el9_2": "pkg:rpm/redhat/kernel-rt-debug@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-0:5.14.0-70.93.1.rt21.165.el9_0": "pkg:rpm/redhat/kernel-rt-debug@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-core": "pkg:rpm/redhat/kernel-rt-debug-core?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-core-0:4.18.0-193.128.1.rt13.179.el8_2":
        "pkg:rpm/redhat/kernel-rt-debug-core@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-core-0:4.18.0-305.125.1.rt7.201.el8_4":
        "pkg:rpm/redhat/kernel-rt-debug-core@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-core-0:4.18.0-513.18.1.rt7.320.el8_9":
        "pkg:rpm/redhat/kernel-rt-debug-core@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-core-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-debug-core@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-core-0:5.14.0-70.93.1.rt21.165.el9_0":
        "pkg:rpm/redhat/kernel-rt-debug-core@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-debuginfo": "pkg:rpm/redhat/kernel-rt-debug-debuginfo?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-devel": "pkg:rpm/redhat/kernel-rt-debug-devel?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-devel-matched": "pkg:rpm/redhat/kernel-rt-debug-devel-matched?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-kvm": "pkg:rpm/redhat/kernel-rt-debug-kvm?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-kvm-0:4.18.0-193.128.1.rt13.179.el8_2":
        "pkg:rpm/redhat/kernel-rt-debug-kvm@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-kvm-0:4.18.0-305.125.1.rt7.201.el8_4":
        "pkg:rpm/redhat/kernel-rt-debug-kvm@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-kvm-0:4.18.0-513.18.1.rt7.320.el8_9":
        "pkg:rpm/redhat/kernel-rt-debug-kvm@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-kvm-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-debug-kvm@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-kvm-0:5.14.0-70.93.1.rt21.165.el9_0":
        "pkg:rpm/redhat/kernel-rt-debug-kvm@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-kvm-debuginfo": "pkg:rpm/redhat/kernel-rt-debug-kvm-debuginfo?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules": "pkg:rpm/redhat/kernel-rt-debug-modules?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-0:4.18.0-193.128.1.rt13.179.el8_2":
        "pkg:rpm/redhat/kernel-rt-debug-modules@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-0:4.18.0-305.125.1.rt7.201.el8_4":
        "pkg:rpm/redhat/kernel-rt-debug-modules@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-0:4.18.0-513.18.1.rt7.320.el8_9":
        "pkg:rpm/redhat/kernel-rt-debug-modules@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-debug-modules@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-0:5.14.0-70.93.1.rt21.165.el9_0":
        "pkg:rpm/redhat/kernel-rt-debug-modules@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-core": "pkg:rpm/redhat/kernel-rt-debug-modules-core?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-core-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-debug-modules-core@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-extra": "pkg:rpm/redhat/kernel-rt-debug-modules-extra?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-extra-0:4.18.0-193.128.1.rt13.179.el8_2":
        "pkg:rpm/redhat/kernel-rt-debug-modules-extra@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-extra-0:4.18.0-305.125.1.rt7.201.el8_4":
        "pkg:rpm/redhat/kernel-rt-debug-modules-extra@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-extra-0:4.18.0-513.18.1.rt7.320.el8_9":
        "pkg:rpm/redhat/kernel-rt-debug-modules-extra@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-extra-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-debug-modules-extra@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-extra-0:5.14.0-70.93.1.rt21.165.el9_0":
        "pkg:rpm/redhat/kernel-rt-debug-modules-extra@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-internal": "pkg:rpm/redhat/kernel-rt-debug-modules-internal?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debug-modules-partner": "pkg:rpm/redhat/kernel-rt-debug-modules-partner?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debuginfo": "pkg:rpm/redhat/kernel-rt-debuginfo?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debuginfo-common-x86_64": "pkg:rpm/redhat/kernel-rt-debuginfo-common-x86_64?upstream=kernel-rt",
    "kernel-rt/kernel-rt-debuginfo-common-x86_64-0:4.18.0-193.128.1.rt13.179.el8_2":
        "pkg:rpm/redhat/kernel-rt-debuginfo-common-x86_64@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debuginfo-common-x86_64-0:4.18.0-305.125.1.rt7.201.el8_4":
        "pkg:rpm/redhat/kernel-rt-debuginfo-common-x86_64@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debuginfo-common-x86_64-0:4.18.0-513.18.1.rt7.320.el8_9":
        "pkg:rpm/redhat/kernel-rt-debuginfo-common-x86_64@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debuginfo-common-x86_64-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-debuginfo-common-x86_64@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-debuginfo-common-x86_64-0:5.14.0-70.93.1.rt21.165.el9_0":
        "pkg:rpm/redhat/kernel-rt-debuginfo-common-x86_64@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-devel": "pkg:rpm/redhat/kernel-rt-devel?upstream=kernel-rt",
    "kernel-rt/kernel-rt-devel-matched": "pkg:rpm/redhat/kernel-rt-devel-matched?upstream=kernel-rt",
    "kernel-rt/kernel-rt-doc": "pkg:rpm/redhat/kernel-rt-doc?upstream=kernel-rt",
    "kernel-rt/kernel-rt-kmap-internal": "pkg:rpm/redhat/kernel-rt-kmap-internal?upstream=kernel-rt",
    "kernel-rt/kernel-rt-kvm": "pkg:rpm/redhat/kernel-rt-kvm?upstream=kernel-rt",
    "kernel-rt/kernel-rt-kvm-0:4.18.0-193.128.1.rt13.179.el8_2": "pkg:rpm/redhat/kernel-rt-kvm@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-kvm-0:4.18.0-305.125.1.rt7.201.el8_4": "pkg:rpm/redhat/kernel-rt-kvm@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-kvm-0:4.18.0-513.18.1.rt7.320.el8_9": "pkg:rpm/redhat/kernel-rt-kvm@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-kvm-0:5.14.0-284.52.1.rt14.337.el9_2": "pkg:rpm/redhat/kernel-rt-kvm@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-kvm-0:5.14.0-70.93.1.rt21.165.el9_0": "pkg:rpm/redhat/kernel-rt-kvm@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-kvm-debuginfo": "pkg:rpm/redhat/kernel-rt-kvm-debuginfo?upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules": "pkg:rpm/redhat/kernel-rt-modules?upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-0:4.18.0-193.128.1.rt13.179.el8_2":
        "pkg:rpm/redhat/kernel-rt-modules@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-0:4.18.0-305.125.1.rt7.201.el8_4":
        "pkg:rpm/redhat/kernel-rt-modules@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-0:4.18.0-513.18.1.rt7.320.el8_9": "pkg:rpm/redhat/kernel-rt-modules@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-modules@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-0:5.14.0-70.93.1.rt21.165.el9_0": "pkg:rpm/redhat/kernel-rt-modules@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-core": "pkg:rpm/redhat/kernel-rt-modules-core?upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-core-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-modules-core@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-extra": "pkg:rpm/redhat/kernel-rt-modules-extra?upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-extra-0:4.18.0-193.128.1.rt13.179.el8_2":
        "pkg:rpm/redhat/kernel-rt-modules-extra@4.18.0-193.128.1.rt13.179.el8_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-extra-0:4.18.0-305.125.1.rt7.201.el8_4":
        "pkg:rpm/redhat/kernel-rt-modules-extra@4.18.0-305.125.1.rt7.201.el8_4?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-extra-0:4.18.0-513.18.1.rt7.320.el8_9":
        "pkg:rpm/redhat/kernel-rt-modules-extra@4.18.0-513.18.1.rt7.320.el8_9?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-extra-0:5.14.0-284.52.1.rt14.337.el9_2":
        "pkg:rpm/redhat/kernel-rt-modules-extra@5.14.0-284.52.1.rt14.337.el9_2?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-extra-0:5.14.0-70.93.1.rt21.165.el9_0":
        "pkg:rpm/redhat/kernel-rt-modules-extra@5.14.0-70.93.1.rt21.165.el9_0?epoch=0&upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-internal": "pkg:rpm/redhat/kernel-rt-modules-internal?upstream=kernel-rt",
    "kernel-rt/kernel-rt-modules-partner": "pkg:rpm/redhat/kernel-rt-modules-partner?upstream=kernel-rt",
    "kernel-rt/kernel-rt-selftests-internal": "pkg:rpm/redhat/kernel-rt-selftests-internal?upstream=kernel-rt",
    "kernel-rt/kernel-rt-trace": "pkg:rpm/redhat/kernel-rt-trace?upstream=kernel-rt",
    "kernel-rt/kernel-rt-trace-debuginfo": "pkg:rpm/redhat/kernel-rt-trace-debuginfo?upstream=kernel-rt",
    "kernel-rt/kernel-rt-trace-devel": "pkg:rpm/redhat/kernel-rt-trace-devel?upstream=kernel-rt",
    "kernel-rt/kernel-rt-trace-kvm": "pkg:rpm/redhat/kernel-rt-trace-kvm?upstream=kernel-rt",
    "kernel-rt/kernel-rt-trace-kvm-debuginfo": "pkg:rpm/redhat/kernel-rt-trace-kvm-debuginfo?upstream=kernel-rt",
    "kernel.src": "pkg:rpm/redhat/kernel?arch=src",
    "kernel/bpftool": "pkg:rpm/redhat/bpftool?upstream=kernel",
    "kernel/bpftool-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/bpftool@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/bpftool-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/bpftool@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/bpftool-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/bpftool@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/bpftool-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/bpftool@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/bpftool-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/bpftool@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/bpftool-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/bpftool@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/bpftool-0:7.0.0-284.52.1.el9_2": "pkg:rpm/redhat/bpftool@7.0.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/bpftool-0:7.2.0-362.24.1.el9_3": "pkg:rpm/redhat/bpftool@7.2.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/bpftool-debuginfo": "pkg:rpm/redhat/bpftool-debuginfo?upstream=kernel",
    "kernel/kernel": "pkg:rpm/redhat/kernel?upstream=kernel",
    "kernel/kernel-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-64k": "pkg:rpm/redhat/kernel-64k?upstream=kernel",
    "kernel/kernel-64k-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-core": "pkg:rpm/redhat/kernel-64k-core?upstream=kernel",
    "kernel/kernel-64k-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug": "pkg:rpm/redhat/kernel-64k-debug?upstream=kernel",
    "kernel/kernel-64k-debug-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k-debug@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k-debug@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-core": "pkg:rpm/redhat/kernel-64k-debug-core?upstream=kernel",
    "kernel/kernel-64k-debug-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k-debug-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k-debug-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-debuginfo": "pkg:rpm/redhat/kernel-64k-debug-debuginfo?upstream=kernel",
    "kernel/kernel-64k-debug-devel": "pkg:rpm/redhat/kernel-64k-debug-devel?upstream=kernel",
    "kernel/kernel-64k-debug-devel-matched": "pkg:rpm/redhat/kernel-64k-debug-devel-matched?upstream=kernel",
    "kernel/kernel-64k-debug-modules": "pkg:rpm/redhat/kernel-64k-debug-modules?upstream=kernel",
    "kernel/kernel-64k-debug-modules-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k-debug-modules@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-modules-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k-debug-modules@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-modules-core": "pkg:rpm/redhat/kernel-64k-debug-modules-core?upstream=kernel",
    "kernel/kernel-64k-debug-modules-core-0:5.14.0-284.52.1.el9_2":
        "pkg:rpm/redhat/kernel-64k-debug-modules-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-modules-core-0:5.14.0-362.24.1.el9_3":
        "pkg:rpm/redhat/kernel-64k-debug-modules-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-modules-extra": "pkg:rpm/redhat/kernel-64k-debug-modules-extra?upstream=kernel",
    "kernel/kernel-64k-debug-modules-extra-0:5.14.0-284.52.1.el9_2":
        "pkg:rpm/redhat/kernel-64k-debug-modules-extra@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-modules-extra-0:5.14.0-362.24.1.el9_3":
        "pkg:rpm/redhat/kernel-64k-debug-modules-extra@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-debug-modules-internal": "pkg:rpm/redhat/kernel-64k-debug-modules-internal?upstream=kernel",
    "kernel/kernel-64k-debug-modules-partner": "pkg:rpm/redhat/kernel-64k-debug-modules-partner?upstream=kernel",
    "kernel/kernel-64k-debuginfo": "pkg:rpm/redhat/kernel-64k-debuginfo?upstream=kernel",
    "kernel/kernel-64k-devel": "pkg:rpm/redhat/kernel-64k-devel?upstream=kernel",
    "kernel/kernel-64k-devel-matched": "pkg:rpm/redhat/kernel-64k-devel-matched?upstream=kernel",
    "kernel/kernel-64k-modules": "pkg:rpm/redhat/kernel-64k-modules?upstream=kernel",
    "kernel/kernel-64k-modules-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k-modules@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-modules-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k-modules@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-modules-core": "pkg:rpm/redhat/kernel-64k-modules-core?upstream=kernel",
    "kernel/kernel-64k-modules-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k-modules-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-modules-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k-modules-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-modules-extra": "pkg:rpm/redhat/kernel-64k-modules-extra?upstream=kernel",
    "kernel/kernel-64k-modules-extra-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-64k-modules-extra@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-64k-modules-extra-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-64k-modules-extra@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-64k-modules-internal": "pkg:rpm/redhat/kernel-64k-modules-internal?upstream=kernel",
    "kernel/kernel-64k-modules-partner": "pkg:rpm/redhat/kernel-64k-modules-partner?upstream=kernel",
    "kernel/kernel-abi-stablelists": "pkg:rpm/redhat/kernel-abi-stablelists?upstream=kernel",
    "kernel/kernel-abi-stablelists-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-abi-stablelists@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-abi-stablelists-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-abi-stablelists@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-abi-stablelists-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-abi-stablelists@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-abi-stablelists-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-abi-stablelists@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-abi-stablelists-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-abi-stablelists@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-abi-stablelists-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-abi-stablelists@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-abi-stablelists-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-abi-stablelists@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-abi-whitelists": "pkg:rpm/redhat/kernel-abi-whitelists?upstream=kernel",
    "kernel/kernel-abi-whitelists-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-abi-whitelists@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-bootwrapper": "pkg:rpm/redhat/kernel-bootwrapper?upstream=kernel",
    "kernel/kernel-core": "pkg:rpm/redhat/kernel-core?upstream=kernel",
    "kernel/kernel-core-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-core@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-core-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-core@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-core-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-core@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-core-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-core@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-core-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-core@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-core-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-core@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-cross-headers": "pkg:rpm/redhat/kernel-cross-headers?upstream=kernel",
    "kernel/kernel-debug": "pkg:rpm/redhat/kernel-debug?upstream=kernel",
    "kernel/kernel-debug-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-debug@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-debug@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-debug-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-debug@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debug-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-debug@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debug-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-debug@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debug-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-debug@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-debug@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debug-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-debug@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core": "pkg:rpm/redhat/kernel-debug-core?upstream=kernel",
    "kernel/kernel-debug-core-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-debug-core@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-debug-core@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-debug-core@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-debug-core@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-debug-core@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-debug-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-debug-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debug-core-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-debug-core@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debug-debuginfo": "pkg:rpm/redhat/kernel-debug-debuginfo?upstream=kernel",
    "kernel/kernel-debug-devel": "pkg:rpm/redhat/kernel-debug-devel?upstream=kernel",
    "kernel/kernel-debug-devel-matched": "pkg:rpm/redhat/kernel-debug-devel-matched?upstream=kernel",
    "kernel/kernel-debug-devel-matched-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-debug-devel-matched@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules": "pkg:rpm/redhat/kernel-debug-modules?upstream=kernel",
    "kernel/kernel-debug-modules-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-debug-modules@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-debug-modules@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-debug-modules@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-debug-modules@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-debug-modules@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-debug-modules@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-debug-modules@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-debug-modules@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-core": "pkg:rpm/redhat/kernel-debug-modules-core?upstream=kernel",
    "kernel/kernel-debug-modules-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-debug-modules-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-debug-modules-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra": "pkg:rpm/redhat/kernel-debug-modules-extra?upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-debug-modules-extra@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-debug-modules-extra@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-debug-modules-extra@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-debug-modules-extra@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-debug-modules-extra@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-debug-modules-extra@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-debug-modules-extra@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-extra-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-debug-modules-extra@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debug-modules-internal": "pkg:rpm/redhat/kernel-debug-modules-internal?upstream=kernel",
    "kernel/kernel-debug-modules-partner": "pkg:rpm/redhat/kernel-debug-modules-partner?upstream=kernel",
    "kernel/kernel-debug-uki-virt": "pkg:rpm/redhat/kernel-debug-uki-virt?upstream=kernel",
    "kernel/kernel-debug-uki-virt-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-debug-uki-virt@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debug-uki-virt-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-debug-uki-virt@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo": "pkg:rpm/redhat/kernel-debuginfo?upstream=kernel",
    "kernel/kernel-debuginfo-common-aarch64": "pkg:rpm/redhat/kernel-debuginfo-common-aarch64?upstream=kernel",
    "kernel/kernel-debuginfo-common-aarch64-0:4.18.0-372.91.1.el8_6":
        "pkg:rpm/redhat/kernel-debuginfo-common-aarch64@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-aarch64-0:4.18.0-477.51.1.el8_8":
        "pkg:rpm/redhat/kernel-debuginfo-common-aarch64@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-aarch64-0:4.18.0-513.18.1.el8_9":
        "pkg:rpm/redhat/kernel-debuginfo-common-aarch64@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-aarch64-0:5.14.0-284.52.1.el9_2":
        "pkg:rpm/redhat/kernel-debuginfo-common-aarch64@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-aarch64-0:5.14.0-362.24.1.el9_3":
        "pkg:rpm/redhat/kernel-debuginfo-common-aarch64@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-aarch64-0:5.14.0-70.93.2.el9_0":
        "pkg:rpm/redhat/kernel-debuginfo-common-aarch64@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-i686": "pkg:rpm/redhat/kernel-debuginfo-common-i686?upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64": "pkg:rpm/redhat/kernel-debuginfo-common-ppc64?upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le": "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le?upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:4.18.0-193.128.1.el8_2":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:4.18.0-305.125.1.el8_4":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:4.18.0-372.91.1.el8_6":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:4.18.0-477.51.1.el8_8":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:4.18.0-513.18.1.el8_9":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:5.14.0-284.52.1.el9_2":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:5.14.0-362.24.1.el9_3":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-ppc64le-0:5.14.0-70.93.2.el9_0":
        "pkg:rpm/redhat/kernel-debuginfo-common-ppc64le@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-s390x": "pkg:rpm/redhat/kernel-debuginfo-common-s390x?upstream=kernel",
    "kernel/kernel-debuginfo-common-s390x-0:4.18.0-372.91.1.el8_6":
        "pkg:rpm/redhat/kernel-debuginfo-common-s390x@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-s390x-0:4.18.0-477.51.1.el8_8":
        "pkg:rpm/redhat/kernel-debuginfo-common-s390x@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-s390x-0:4.18.0-513.18.1.el8_9":
        "pkg:rpm/redhat/kernel-debuginfo-common-s390x@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-s390x-0:5.14.0-284.52.1.el9_2":
        "pkg:rpm/redhat/kernel-debuginfo-common-s390x@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-s390x-0:5.14.0-362.24.1.el9_3":
        "pkg:rpm/redhat/kernel-debuginfo-common-s390x@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-s390x-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-debuginfo-common-s390x@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64": "pkg:rpm/redhat/kernel-debuginfo-common-x86_64?upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:4.18.0-193.128.1.el8_2":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:4.18.0-305.125.1.el8_4":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:4.18.0-372.91.1.el8_6":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:4.18.0-477.51.1.el8_8":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:4.18.0-513.18.1.el8_9":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:5.14.0-284.52.1.el9_2":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:5.14.0-362.24.1.el9_3":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-debuginfo-common-x86_64-0:5.14.0-70.93.2.el9_0":
        "pkg:rpm/redhat/kernel-debuginfo-common-x86_64@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-devel": "pkg:rpm/redhat/kernel-devel?upstream=kernel",
    "kernel/kernel-devel-matched": "pkg:rpm/redhat/kernel-devel-matched?upstream=kernel",
    "kernel/kernel-devel-matched-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-devel-matched@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-doc": "pkg:rpm/redhat/kernel-doc?upstream=kernel",
    "kernel/kernel-firmware": "pkg:rpm/redhat/kernel-firmware?upstream=kernel",
    "kernel/kernel-headers": "pkg:rpm/redhat/kernel-headers?upstream=kernel",
    "kernel/kernel-ipaclones-internal": "pkg:rpm/redhat/kernel-ipaclones-internal?upstream=kernel",
    "kernel/kernel-kdump": "pkg:rpm/redhat/kernel-kdump?upstream=kernel",
    "kernel/kernel-kdump-debuginfo": "pkg:rpm/redhat/kernel-kdump-debuginfo?upstream=kernel",
    "kernel/kernel-kdump-devel": "pkg:rpm/redhat/kernel-kdump-devel?upstream=kernel",
    "kernel/kernel-kmap-internal": "pkg:rpm/redhat/kernel-kmap-internal?upstream=kernel",
    "kernel/kernel-modules": "pkg:rpm/redhat/kernel-modules?upstream=kernel",
    "kernel/kernel-modules-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-modules@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-modules-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-modules@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-modules-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-modules@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-modules-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-modules@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-modules-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-modules@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-modules-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-modules@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-modules-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-modules@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-modules-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-modules@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-modules-core": "pkg:rpm/redhat/kernel-modules-core?upstream=kernel",
    "kernel/kernel-modules-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-modules-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-modules-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-modules-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra": "pkg:rpm/redhat/kernel-modules-extra?upstream=kernel",
    "kernel/kernel-modules-extra-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-modules-extra@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-modules-extra@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-modules-extra@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-modules-extra@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-modules-extra@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-modules-extra@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-modules-extra@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-modules-extra-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-modules-extra@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-modules-internal": "pkg:rpm/redhat/kernel-modules-internal?upstream=kernel",
    "kernel/kernel-modules-partner": "pkg:rpm/redhat/kernel-modules-partner?upstream=kernel",
    "kernel/kernel-rt": "pkg:rpm/redhat/kernel-rt?upstream=kernel",
    "kernel/kernel-rt-64k": "pkg:rpm/redhat/kernel-rt-64k?upstream=kernel",
    "kernel/kernel-rt-64k-core": "pkg:rpm/redhat/kernel-rt-64k-core?upstream=kernel",
    "kernel/kernel-rt-64k-debug": "pkg:rpm/redhat/kernel-rt-64k-debug?upstream=kernel",
    "kernel/kernel-rt-64k-debug-core": "pkg:rpm/redhat/kernel-rt-64k-debug-core?upstream=kernel",
    "kernel/kernel-rt-64k-debug-debuginfo": "pkg:rpm/redhat/kernel-rt-64k-debug-debuginfo?upstream=kernel",
    "kernel/kernel-rt-64k-debug-devel": "pkg:rpm/redhat/kernel-rt-64k-debug-devel?upstream=kernel",
    "kernel/kernel-rt-64k-debug-modules": "pkg:rpm/redhat/kernel-rt-64k-debug-modules?upstream=kernel",
    "kernel/kernel-rt-64k-debug-modules-core": "pkg:rpm/redhat/kernel-rt-64k-debug-modules-core?upstream=kernel",
    "kernel/kernel-rt-64k-debug-modules-extra": "pkg:rpm/redhat/kernel-rt-64k-debug-modules-extra?upstream=kernel",
    "kernel/kernel-rt-64k-debuginfo": "pkg:rpm/redhat/kernel-rt-64k-debuginfo?upstream=kernel",
    "kernel/kernel-rt-64k-devel": "pkg:rpm/redhat/kernel-rt-64k-devel?upstream=kernel",
    "kernel/kernel-rt-64k-modules": "pkg:rpm/redhat/kernel-rt-64k-modules?upstream=kernel",
    "kernel/kernel-rt-64k-modules-core": "pkg:rpm/redhat/kernel-rt-64k-modules-core?upstream=kernel",
    "kernel/kernel-rt-64k-modules-extra": "pkg:rpm/redhat/kernel-rt-64k-modules-extra?upstream=kernel",
    "kernel/kernel-rt-core": "pkg:rpm/redhat/kernel-rt-core?upstream=kernel",
    "kernel/kernel-rt-debug": "pkg:rpm/redhat/kernel-rt-debug?upstream=kernel",
    "kernel/kernel-rt-debug-core": "pkg:rpm/redhat/kernel-rt-debug-core?upstream=kernel",
    "kernel/kernel-rt-debug-debuginfo": "pkg:rpm/redhat/kernel-rt-debug-debuginfo?upstream=kernel",
    "kernel/kernel-rt-debug-devel": "pkg:rpm/redhat/kernel-rt-debug-devel?upstream=kernel",
    "kernel/kernel-rt-debug-kvm": "pkg:rpm/redhat/kernel-rt-debug-kvm?upstream=kernel",
    "kernel/kernel-rt-debug-modules": "pkg:rpm/redhat/kernel-rt-debug-modules?upstream=kernel",
    "kernel/kernel-rt-debug-modules-core": "pkg:rpm/redhat/kernel-rt-debug-modules-core?upstream=kernel",
    "kernel/kernel-rt-debug-modules-extra": "pkg:rpm/redhat/kernel-rt-debug-modules-extra?upstream=kernel",
    "kernel/kernel-rt-debuginfo": "pkg:rpm/redhat/kernel-rt-debuginfo?upstream=kernel",
    "kernel/kernel-rt-devel": "pkg:rpm/redhat/kernel-rt-devel?upstream=kernel",
    "kernel/kernel-rt-kvm": "pkg:rpm/redhat/kernel-rt-kvm?upstream=kernel",
    "kernel/kernel-rt-modules": "pkg:rpm/redhat/kernel-rt-modules?upstream=kernel",
    "kernel/kernel-rt-modules-core": "pkg:rpm/redhat/kernel-rt-modules-core?upstream=kernel",
    "kernel/kernel-rt-modules-extra": "pkg:rpm/redhat/kernel-rt-modules-extra?upstream=kernel",
    "kernel/kernel-selftests-internal": "pkg:rpm/redhat/kernel-selftests-internal?upstream=kernel",
    "kernel/kernel-tools": "pkg:rpm/redhat/kernel-tools?upstream=kernel",
    "kernel/kernel-tools-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-tools@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-tools-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-tools@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-tools-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-tools@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-tools-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-tools@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-tools-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-tools@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-tools-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-tools@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-tools-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-tools@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-tools-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-tools@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-tools-debuginfo": "pkg:rpm/redhat/kernel-tools-debuginfo?upstream=kernel",
    "kernel/kernel-tools-libs": "pkg:rpm/redhat/kernel-tools-libs?upstream=kernel",
    "kernel/kernel-tools-libs-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/kernel-tools-libs@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/kernel-tools-libs@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-tools-libs@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-tools-libs@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-tools-libs@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-tools-libs@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-tools-libs@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-tools-libs@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-tools-libs-devel": "pkg:rpm/redhat/kernel-tools-libs-devel?upstream=kernel",
    "kernel/kernel-uki-virt": "pkg:rpm/redhat/kernel-uki-virt?upstream=kernel",
    "kernel/kernel-uki-virt-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-uki-virt@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-uki-virt-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-uki-virt@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-uki-virt-addons": "pkg:rpm/redhat/kernel-uki-virt-addons?upstream=kernel",
    "kernel/kernel-zfcpdump": "pkg:rpm/redhat/kernel-zfcpdump?upstream=kernel",
    "kernel/kernel-zfcpdump-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-zfcpdump@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-zfcpdump@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-zfcpdump@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-zfcpdump@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-zfcpdump@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-zfcpdump@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-core": "pkg:rpm/redhat/kernel-zfcpdump-core?upstream=kernel",
    "kernel/kernel-zfcpdump-core-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-zfcpdump-core@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-core-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-zfcpdump-core@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-core-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-zfcpdump-core@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-zfcpdump-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-zfcpdump-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-core-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-zfcpdump-core@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-debuginfo": "pkg:rpm/redhat/kernel-zfcpdump-debuginfo?upstream=kernel",
    "kernel/kernel-zfcpdump-devel": "pkg:rpm/redhat/kernel-zfcpdump-devel?upstream=kernel",
    "kernel/kernel-zfcpdump-devel-matched": "pkg:rpm/redhat/kernel-zfcpdump-devel-matched?upstream=kernel",
    "kernel/kernel-zfcpdump-devel-matched-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-zfcpdump-devel-matched@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules": "pkg:rpm/redhat/kernel-zfcpdump-modules?upstream=kernel",
    "kernel/kernel-zfcpdump-modules-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/kernel-zfcpdump-modules@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/kernel-zfcpdump-modules@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/kernel-zfcpdump-modules@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-zfcpdump-modules@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-zfcpdump-modules@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-zfcpdump-modules@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-core": "pkg:rpm/redhat/kernel-zfcpdump-modules-core?upstream=kernel",
    "kernel/kernel-zfcpdump-modules-core-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/kernel-zfcpdump-modules-core@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-core-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/kernel-zfcpdump-modules-core@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-extra": "pkg:rpm/redhat/kernel-zfcpdump-modules-extra?upstream=kernel",
    "kernel/kernel-zfcpdump-modules-extra-0:4.18.0-372.91.1.el8_6":
        "pkg:rpm/redhat/kernel-zfcpdump-modules-extra@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-extra-0:4.18.0-477.51.1.el8_8":
        "pkg:rpm/redhat/kernel-zfcpdump-modules-extra@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-extra-0:4.18.0-513.18.1.el8_9":
        "pkg:rpm/redhat/kernel-zfcpdump-modules-extra@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-extra-0:5.14.0-284.52.1.el9_2":
        "pkg:rpm/redhat/kernel-zfcpdump-modules-extra@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-extra-0:5.14.0-362.24.1.el9_3":
        "pkg:rpm/redhat/kernel-zfcpdump-modules-extra@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-extra-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/kernel-zfcpdump-modules-extra@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/kernel-zfcpdump-modules-internal": "pkg:rpm/redhat/kernel-zfcpdump-modules-internal?upstream=kernel",
    "kernel/kernel-zfcpdump-modules-partner": "pkg:rpm/redhat/kernel-zfcpdump-modules-partner?upstream=kernel",
    "kernel/libperf": "pkg:rpm/redhat/libperf?upstream=kernel",
    "kernel/libperf-debuginfo": "pkg:rpm/redhat/libperf-debuginfo?upstream=kernel",
    "kernel/perf": "pkg:rpm/redhat/perf?upstream=kernel",
    "kernel/perf-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/perf@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/perf-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/perf@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/perf-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/perf@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/perf-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/perf@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/perf-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/perf@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/perf-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/perf@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/perf-debuginfo": "pkg:rpm/redhat/perf-debuginfo?upstream=kernel",
    "kernel/python-perf": "pkg:rpm/redhat/python-perf?upstream=kernel",
    "kernel/python-perf-debuginfo": "pkg:rpm/redhat/python-perf-debuginfo?upstream=kernel",
    "kernel/python3-perf": "pkg:rpm/redhat/python3-perf?upstream=kernel",
    "kernel/python3-perf-0:4.18.0-193.128.1.el8_2": "pkg:rpm/redhat/python3-perf@4.18.0-193.128.1.el8_2?epoch=0&upstream=kernel",
    "kernel/python3-perf-0:4.18.0-305.125.1.el8_4": "pkg:rpm/redhat/python3-perf@4.18.0-305.125.1.el8_4?epoch=0&upstream=kernel",
    "kernel/python3-perf-0:4.18.0-372.91.1.el8_6": "pkg:rpm/redhat/python3-perf@4.18.0-372.91.1.el8_6?epoch=0&upstream=kernel",
    "kernel/python3-perf-0:4.18.0-477.51.1.el8_8": "pkg:rpm/redhat/python3-perf@4.18.0-477.51.1.el8_8?epoch=0&upstream=kernel",
    "kernel/python3-perf-0:4.18.0-513.18.1.el8_9": "pkg:rpm/redhat/python3-perf@4.18.0-513.18.1.el8_9?epoch=0&upstream=kernel",
    "kernel/python3-perf-0:5.14.0-284.52.1.el9_2": "pkg:rpm/redhat/python3-perf@5.14.0-284.52.1.el9_2?epoch=0&upstream=kernel",
    "kernel/python3-perf-0:5.14.0-362.24.1.el9_3": "pkg:rpm/redhat/python3-perf@5.14.0-362.24.1.el9_3?epoch=0&upstream=kernel",
    "kernel/python3-perf-0:5.14.0-70.93.2.el9_0": "pkg:rpm/redhat/python3-perf@5.14.0-70.93.2.el9_0?epoch=0&upstream=kernel",
    "kernel/python3-perf-debuginfo": "pkg:rpm/redhat/python3-perf-debuginfo?upstream=kernel",
    "kernel/rtla": "pkg:rpm/redhat/rtla?upstream=kernel",
    "kernel/rv": "pkg:rpm/redhat/rv?upstream=kernel",
    "kpatch-patch-0:4_18_0-193_120_1-1-1.el8_2.src": "pkg:rpm/redhat/kpatch-patch@4_18_0-193_120_1-1-1.el8_2?arch=src&epoch=0",
    "kpatch-patch-0:4_18_0-305_120_1-1-1.el8_4.src": "pkg:rpm/redhat/kpatch-patch@4_18_0-305_120_1-1-1.el8_4?arch=src&epoch=0",
    "kpatch-patch-0:4_18_0-372_87_1-1-1.el8_6.src": "pkg:rpm/redhat/kpatch-patch@4_18_0-372_87_1-1-1.el8_6?arch=src&epoch=0",
    "kpatch-patch-0:4_18_0-477_43_1-1-1.el8_8.src": "pkg:rpm/redhat/kpatch-patch@4_18_0-477_43_1-1-1.el8_8?arch=src&epoch=0",
    "kpatch-patch-0:4_18_0-513_11_1-1-1.el8_9.src": "pkg:rpm/redhat/kpatch-patch@4_18_0-513_11_1-1-1.el8_9?arch=src&epoch=0",
    "kpatch-patch-0:5_14_0-284_48_1-1-1.el9_2.src": "pkg:rpm/redhat/kpatch-patch@5_14_0-284_48_1-1-1.el9_2?arch=src&epoch=0",
    "kpatch-patch-5_14_0-362_13_1-0:5_14_0-362_13_1-1-2.el9_3.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-362_13_1@5_14_0-362_13_1-1-2.el9_3?arch=src&epoch=0",
    "kpatch-patch-5_14_0-362_13_1/kpatch-patch-5_14_0-362_13_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-362_13_1?upstream=kpatch-patch-5_14_0-362_13_1",
    "kpatch-patch-5_14_0-362_13_1/kpatch-patch-5_14_0-362_13_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-362_13_1-debuginfo?upstream=kpatch-patch-5_14_0-362_13_1",
    "kpatch-patch-5_14_0-362_13_1/kpatch-patch-5_14_0-362_13_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-362_13_1-debugsource?upstream=kpatch-patch-5_14_0-362_13_1",
    "kpatch-patch-5_14_0-362_18_1-0:5_14_0-362_18_1-1-1.el9_3.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-362_18_1@5_14_0-362_18_1-1-1.el9_3?arch=src&epoch=0",
    "kpatch-patch-5_14_0-362_18_1/kpatch-patch-5_14_0-362_18_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-362_18_1?upstream=kpatch-patch-5_14_0-362_18_1",
    "kpatch-patch-5_14_0-362_18_1/kpatch-patch-5_14_0-362_18_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-362_18_1-debuginfo?upstream=kpatch-patch-5_14_0-362_18_1",
    "kpatch-patch-5_14_0-362_18_1/kpatch-patch-5_14_0-362_18_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-362_18_1-debugsource?upstream=kpatch-patch-5_14_0-362_18_1",
    "kpatch-patch-5_14_0-362_8_1-0:5_14_0-362_8_1-1-3.el9_3.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-362_8_1@5_14_0-362_8_1-1-3.el9_3?arch=src&epoch=0",
    "kpatch-patch-5_14_0-362_8_1/kpatch-patch-5_14_0-362_8_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-362_8_1?upstream=kpatch-patch-5_14_0-362_8_1",
    "kpatch-patch-5_14_0-362_8_1/kpatch-patch-5_14_0-362_8_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-362_8_1-debuginfo?upstream=kpatch-patch-5_14_0-362_8_1",
    "kpatch-patch-5_14_0-362_8_1/kpatch-patch-5_14_0-362_8_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-362_8_1-debugsource?upstream=kpatch-patch-5_14_0-362_8_1",
    "kpatch-patch-5_14_0-70_64_1-0:5_14_0-70_64_1-1-6.el9_0.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_64_1@5_14_0-70_64_1-1-6.el9_0?arch=src&epoch=0",
    "kpatch-patch-5_14_0-70_64_1/kpatch-patch-5_14_0-70_64_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_64_1?upstream=kpatch-patch-5_14_0-70_64_1",
    "kpatch-patch-5_14_0-70_64_1/kpatch-patch-5_14_0-70_64_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_64_1-debuginfo?upstream=kpatch-patch-5_14_0-70_64_1",
    "kpatch-patch-5_14_0-70_64_1/kpatch-patch-5_14_0-70_64_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_64_1-debugsource?upstream=kpatch-patch-5_14_0-70_64_1",
    "kpatch-patch-5_14_0-70_70_1-0:5_14_0-70_70_1-1-5.el9_0.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_70_1@5_14_0-70_70_1-1-5.el9_0?arch=src&epoch=0",
    "kpatch-patch-5_14_0-70_70_1/kpatch-patch-5_14_0-70_70_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_70_1?upstream=kpatch-patch-5_14_0-70_70_1",
    "kpatch-patch-5_14_0-70_70_1/kpatch-patch-5_14_0-70_70_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_70_1-debuginfo?upstream=kpatch-patch-5_14_0-70_70_1",
    "kpatch-patch-5_14_0-70_70_1/kpatch-patch-5_14_0-70_70_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_70_1-debugsource?upstream=kpatch-patch-5_14_0-70_70_1",
    "kpatch-patch-5_14_0-70_75_1-0:5_14_0-70_75_1-1-4.el9_0.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_75_1@5_14_0-70_75_1-1-4.el9_0?arch=src&epoch=0",
    "kpatch-patch-5_14_0-70_75_1/kpatch-patch-5_14_0-70_75_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_75_1?upstream=kpatch-patch-5_14_0-70_75_1",
    "kpatch-patch-5_14_0-70_75_1/kpatch-patch-5_14_0-70_75_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_75_1-debuginfo?upstream=kpatch-patch-5_14_0-70_75_1",
    "kpatch-patch-5_14_0-70_75_1/kpatch-patch-5_14_0-70_75_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_75_1-debugsource?upstream=kpatch-patch-5_14_0-70_75_1",
    "kpatch-patch-5_14_0-70_80_1-0:5_14_0-70_80_1-1-3.el9_0.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_80_1@5_14_0-70_80_1-1-3.el9_0?arch=src&epoch=0",
    "kpatch-patch-5_14_0-70_80_1/kpatch-patch-5_14_0-70_80_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_80_1?upstream=kpatch-patch-5_14_0-70_80_1",
    "kpatch-patch-5_14_0-70_80_1/kpatch-patch-5_14_0-70_80_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_80_1-debuginfo?upstream=kpatch-patch-5_14_0-70_80_1",
    "kpatch-patch-5_14_0-70_80_1/kpatch-patch-5_14_0-70_80_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_80_1-debugsource?upstream=kpatch-patch-5_14_0-70_80_1",
    "kpatch-patch-5_14_0-70_85_1-0:5_14_0-70_85_1-1-2.el9_0.src": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_85_1@5_14_0-70_85_1-1-2.el9_0?arch=src&epoch=0",
    "kpatch-patch-5_14_0-70_85_1/kpatch-patch-5_14_0-70_85_1": "pkg:rpm/redhat/kpatch-patch-5_14_0-70_85_1?upstream=kpatch-patch-5_14_0-70_85_1",
    "kpatch-patch-5_14_0-70_85_1/kpatch-patch-5_14_0-70_85_1-debuginfo":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_85_1-debuginfo?upstream=kpatch-patch-5_14_0-70_85_1",
    "kpatch-patch-5_14_0-70_85_1/kpatch-patch-5_14_0-70_85_1-debugsource":
        "pkg:rpm/redhat/kpatch-patch-5_14_0-70_85_1-debugsource?upstream=kpatch-patch-5_14_0-70_85_1",
    "kpatch-patch/kpatch-patch-4_18_0-193_113_1-0:1-4.el8_2": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_113_1@1-4.el8_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_113_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_113_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_113_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_113_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_116_1-0:1-3.el8_2": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_116_1@1-3.el8_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_116_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_116_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_116_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_116_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_119_1-0:1-2.el8_2": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_119_1@1-2.el8_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_119_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_119_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_119_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_119_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_120_1-0:1-1.el8_2": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_120_1@1-1.el8_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_120_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_120_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-193_120_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-193_120_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_103_1-0:1-4.el8_4": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_103_1@1-4.el8_4?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_103_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_103_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_103_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_103_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_108_1-0:1-3.el8_4": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_108_1@1-3.el8_4?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_108_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_108_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_108_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_108_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_114_1-0:1-2.el8_4": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_114_1@1-2.el8_4?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_114_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_114_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_114_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_114_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_120_1-0:1-1.el8_4": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_120_1@1-1.el8_4?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_120_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_120_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-305_120_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-305_120_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_64_1-0:1-5.el8_6": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_64_1@1-5.el8_6?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_64_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_64_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_64_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_64_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_70_1-0:1-4.el8_6": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_70_1@1-4.el8_6?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_70_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_70_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_70_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_70_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_75_1-0:1-3.el8_6": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_75_1@1-3.el8_6?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_75_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_75_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_75_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_75_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_80_1-0:1-2.el8_6": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_80_1@1-2.el8_6?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_80_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_80_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_80_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_80_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_87_1-0:1-1.el8_6": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_87_1@1-1.el8_6?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_87_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_87_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-372_87_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-372_87_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_27_1-0:1-3.el8_8": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_27_1@1-3.el8_8?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_27_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_27_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_27_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_27_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_36_1-0:1-2.el8_8": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_36_1@1-2.el8_8?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_36_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_36_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_36_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_36_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_43_1-0:1-1.el8_8": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_43_1@1-1.el8_8?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_43_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_43_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-477_43_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-477_43_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_11_1-0:1-1.el8_9": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_11_1@1-1.el8_9?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_11_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_11_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_11_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_11_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_5_1-0:1-3.el8_9": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_5_1@1-3.el8_9?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_5_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_5_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_5_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_5_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_9_1-0:1-2.el8_9": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_9_1@1-2.el8_9?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_9_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_9_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-4_18_0-513_9_1-debugsource": "pkg:rpm/redhat/kpatch-patch-4_18_0-513_9_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_25_1-0:1-6.el9_2": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_25_1@1-6.el9_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_25_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_25_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_25_1-debugsource": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_25_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_30_1-0:1-3.el9_2": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_30_1@1-3.el9_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_30_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_30_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_30_1-debugsource": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_30_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_40_1-0:1-2.el9_2": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_40_1@1-2.el9_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_40_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_40_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_40_1-debugsource": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_40_1-debugsource?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_48_1-0:1-1.el9_2": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_48_1@1-1.el9_2?epoch=0&upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_48_1-debuginfo": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_48_1-debuginfo?upstream=kpatch-patch",
    "kpatch-patch/kpatch-patch-5_14_0-284_48_1-debugsource": "pkg:rpm/redhat/kpatch-patch-5_14_0-284_48_1-debugsource?upstream=kpatch-patch",
    "kpatch.src": "pkg:rpm/redhat/kpatch?arch=src",
    "kpatch/kpatch": "pkg:rpm/redhat/kpatch?upstream=kpatch",
    "kpatch/kpatch-dnf": "pkg:rpm/redhat/kpatch-dnf?upstream=kpatch",
    "log-file-metric-exporter-container-v1.1.0-0:227": "pkg:rpm/redhat/log-file-metric-exporter-container-v1.1.0@227?epoch=0",
    "logging-curator5-container-v5.8.1-0:470": "pkg:rpm/redhat/logging-curator5-container-v5.8.1@470?epoch=0",
    "logging-elasticsearch6-container-v6.8.1-0:407": "pkg:rpm/redhat/logging-elasticsearch6-container-v6.8.1@407?epoch=0",
    "logging-eventrouter-container-v0.4.0-0:247": "pkg:rpm/redhat/logging-eventrouter-container-v0.4.0@247?epoch=0",
    "logging-fluentd-container-v5.8.6-0:5": "pkg:rpm/redhat/logging-fluentd-container-v5.8.6@5?epoch=0",
    "logging-loki-container-v2.9.6-0:14": "pkg:rpm/redhat/logging-loki-container-v2.9.6@14?epoch=0",
    "logging-vector-container-v0.28.1-0:56": "pkg:rpm/redhat/logging-vector-container-v0.28.1@56?epoch=0",
    "logging-view-plugin-container-v5.8.6-0:2": "pkg:rpm/redhat/logging-view-plugin-container-v5.8.6@2?epoch=0",
    "loki-operator-bundle-container-v5.8.6-0:24": "pkg:rpm/redhat/loki-operator-bundle-container-v5.8.6@24?epoch=0",
    "loki-operator-container-v5.8.6-0:10": "pkg:rpm/redhat/loki-operator-container-v5.8.6@10?epoch=0",
    "lokistack-gateway-container-v0.1.0-0:525": "pkg:rpm/redhat/lokistack-gateway-container-v0.1.0@525?epoch=0",
    "opa-openshift-container-v0.1.0-0:224": "pkg:rpm/redhat/opa-openshift-container-v0.1.0@224?epoch=0",
    "devspaces/udi-rhel9": "pkg:oci/udi-rhel9?repository_url=registry.redhat.io/devspaces/udi-rhel9",
    "devspaces/udi-rhel9-0:3.25.0": "pkg:oci/udi-rhel9@3.25.0?repository_url=registry.redhat.io/devspaces/udi-rhel9&tag=3.25.0-1765582207",
    "dotnet10.0-0:10.0.100~rc.2.25502.107-0.10.el9_7.src": "pkg:rpm/redhat/dotnet10.0@10.0.100~rc.2.25502.107-0.10.el9_7?arch=src&epoch=0",
    "dotnet10.0-0:10.0.100~rc.2.25502.107-0.12.el10_1.src": "pkg:rpm/redhat/dotnet10.0@10.0.100~rc.2.25502.107-0.12.el10_1?arch=src&epoch=0",
    "dotnet10.0.src": "pkg:rpm/redhat/dotnet10.0?arch=src",
    "dotnet10.0/aspnetcore-runtime-10.0": "pkg:rpm/redhat/aspnetcore-runtime-10.0?upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-runtime-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/aspnetcore-runtime-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-runtime-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/aspnetcore-runtime-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-runtime-dbg-10.0": "pkg:rpm/redhat/aspnetcore-runtime-dbg-10.0?upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-runtime-dbg-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/aspnetcore-runtime-dbg-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-runtime-dbg-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/aspnetcore-runtime-dbg-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-targeting-pack-10.0": "pkg:rpm/redhat/aspnetcore-targeting-pack-10.0?upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-targeting-pack-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/aspnetcore-targeting-pack-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/aspnetcore-targeting-pack-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/aspnetcore-targeting-pack-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-apphost-pack-10.0": "pkg:rpm/redhat/dotnet-apphost-pack-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-apphost-pack-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-apphost-pack-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-apphost-pack-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-apphost-pack-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-apphost-pack-10.0-debuginfo": "pkg:rpm/redhat/dotnet-apphost-pack-10.0-debuginfo?upstream=dotnet10.0",
    "dotnet10.0/dotnet-host": "pkg:rpm/redhat/dotnet-host?upstream=dotnet10.0",
    "dotnet10.0/dotnet-host-0:10.0.0~rc.2.25502.107-0.10.el9_7": "pkg:rpm/redhat/dotnet-host@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-host-0:10.0.0~rc.2.25502.107-0.12.el10_1": "pkg:rpm/redhat/dotnet-host@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-host-debuginfo": "pkg:rpm/redhat/dotnet-host-debuginfo?upstream=dotnet10.0",
    "dotnet10.0/dotnet-hostfxr-10.0": "pkg:rpm/redhat/dotnet-hostfxr-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-hostfxr-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-hostfxr-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-hostfxr-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-hostfxr-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-hostfxr-10.0-debuginfo": "pkg:rpm/redhat/dotnet-hostfxr-10.0-debuginfo?upstream=dotnet10.0",
    "dotnet10.0/dotnet-runtime-10.0": "pkg:rpm/redhat/dotnet-runtime-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-runtime-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-runtime-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-runtime-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-runtime-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-runtime-10.0-debuginfo": "pkg:rpm/redhat/dotnet-runtime-10.0-debuginfo?upstream=dotnet10.0",
    "dotnet10.0/dotnet-runtime-dbg-10.0": "pkg:rpm/redhat/dotnet-runtime-dbg-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-runtime-dbg-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-runtime-dbg-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-runtime-dbg-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-runtime-dbg-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-10.0": "pkg:rpm/redhat/dotnet-sdk-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-10.0-0:10.0.100~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-sdk-10.0@10.0.100~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-10.0-0:10.0.100~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-sdk-10.0@10.0.100~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-10.0-debuginfo": "pkg:rpm/redhat/dotnet-sdk-10.0-debuginfo?upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-10.0-source-built-artifacts": "pkg:rpm/redhat/dotnet-sdk-10.0-source-built-artifacts?upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-10.0-source-built-artifacts-0:10.0.100~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-sdk-10.0-source-built-artifacts@10.0.100~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-10.0-source-built-artifacts-0:10.0.100~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-sdk-10.0-source-built-artifacts@10.0.100~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-aot-10.0": "pkg:rpm/redhat/dotnet-sdk-aot-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-aot-10.0-0:10.0.100~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-sdk-aot-10.0@10.0.100~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-aot-10.0-0:10.0.100~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-sdk-aot-10.0@10.0.100~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-aot-10.0-debuginfo": "pkg:rpm/redhat/dotnet-sdk-aot-10.0-debuginfo?upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-dbg-10.0": "pkg:rpm/redhat/dotnet-sdk-dbg-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-dbg-10.0-0:10.0.100~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-sdk-dbg-10.0@10.0.100~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-sdk-dbg-10.0-0:10.0.100~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-sdk-dbg-10.0@10.0.100~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-targeting-pack-10.0": "pkg:rpm/redhat/dotnet-targeting-pack-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-targeting-pack-10.0-0:10.0.0~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-targeting-pack-10.0@10.0.0~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-targeting-pack-10.0-0:10.0.0~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-targeting-pack-10.0@10.0.0~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-templates-10.0": "pkg:rpm/redhat/dotnet-templates-10.0?upstream=dotnet10.0",
    "dotnet10.0/dotnet-templates-10.0-0:10.0.100~rc.2.25502.107-0.10.el9_7":
        "pkg:rpm/redhat/dotnet-templates-10.0@10.0.100~rc.2.25502.107-0.10.el9_7?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet-templates-10.0-0:10.0.100~rc.2.25502.107-0.12.el10_1":
        "pkg:rpm/redhat/dotnet-templates-10.0@10.0.100~rc.2.25502.107-0.12.el10_1?epoch=0&upstream=dotnet10.0",
    "dotnet10.0/dotnet10.0-debuginfo": "pkg:rpm/redhat/dotnet10.0-debuginfo?upstream=dotnet10.0",
    "dotnet10.0/dotnet10.0-debugsource": "pkg:rpm/redhat/dotnet10.0-debugsource?upstream=dotnet10.0",
    "dotnet6.0.src": "pkg:rpm/redhat/dotnet6.0?arch=src",
    "dotnet6.0/aspnetcore-runtime-6.0": "pkg:rpm/redhat/aspnetcore-runtime-6.0?upstream=dotnet6.0",
    "dotnet6.0/aspnetcore-targeting-pack-6.0": "pkg:rpm/redhat/aspnetcore-targeting-pack-6.0?upstream=dotnet6.0",
    "dotnet6.0/dotnet-apphost-pack-6.0": "pkg:rpm/redhat/dotnet-apphost-pack-6.0?upstream=dotnet6.0",
    "dotnet6.0/dotnet-apphost-pack-6.0-debuginfo": "pkg:rpm/redhat/dotnet-apphost-pack-6.0-debuginfo?upstream=dotnet6.0",
    "dotnet6.0/dotnet-host": "pkg:rpm/redhat/dotnet-host?upstream=dotnet6.0",
    "dotnet6.0/dotnet-host-debuginfo": "pkg:rpm/redhat/dotnet-host-debuginfo?upstream=dotnet6.0",
    "dotnet6.0/dotnet-hostfxr-6.0": "pkg:rpm/redhat/dotnet-hostfxr-6.0?upstream=dotnet6.0",
    "dotnet6.0/dotnet-hostfxr-6.0-debuginfo": "pkg:rpm/redhat/dotnet-hostfxr-6.0-debuginfo?upstream=dotnet6.0",
    "dotnet6.0/dotnet-runtime-6.0": "pkg:rpm/redhat/dotnet-runtime-6.0?upstream=dotnet6.0",
    "dotnet6.0/dotnet-runtime-6.0-debuginfo": "pkg:rpm/redhat/dotnet-runtime-6.0-debuginfo?upstream=dotnet6.0",
    "dotnet6.0/dotnet-sdk-6.0": "pkg:rpm/redhat/dotnet-sdk-6.0?upstream=dotnet6.0",
    "dotnet6.0/dotnet-sdk-6.0-debuginfo": "pkg:rpm/redhat/dotnet-sdk-6.0-debuginfo?upstream=dotnet6.0",
    "dotnet6.0/dotnet-sdk-6.0-source-built-artifacts": "pkg:rpm/redhat/dotnet-sdk-6.0-source-built-artifacts?upstream=dotnet6.0",
    "dotnet6.0/dotnet-targeting-pack-6.0": "pkg:rpm/redhat/dotnet-targeting-pack-6.0?upstream=dotnet6.0",
    "dotnet6.0/dotnet-templates-6.0": "pkg:rpm/redhat/dotnet-templates-6.0?upstream=dotnet6.0",
    "dotnet6.0/dotnet6.0-debuginfo": "pkg:rpm/redhat/dotnet6.0-debuginfo?upstream=dotnet6.0",
    "dotnet6.0/dotnet6.0-debugsource": "pkg:rpm/redhat/dotnet6.0-debugsource?upstream=dotnet6.0",
    "dotnet6.0/netstandard-targeting-pack-2.1": "pkg:rpm/redhat/netstandard-targeting-pack-2.1?upstream=dotnet6.0",
    "dotnet7.0.src": "pkg:rpm/redhat/dotnet7.0?arch=src",
    "dotnet7.0/aspnetcore-runtime-7.0": "pkg:rpm/redhat/aspnetcore-runtime-7.0?upstream=dotnet7.0",
    "dotnet7.0/aspnetcore-targeting-pack-7.0": "pkg:rpm/redhat/aspnetcore-targeting-pack-7.0?upstream=dotnet7.0",
    "dotnet7.0/dotnet-apphost-pack-7.0": "pkg:rpm/redhat/dotnet-apphost-pack-7.0?upstream=dotnet7.0",
    "dotnet7.0/dotnet-apphost-pack-7.0-debuginfo": "pkg:rpm/redhat/dotnet-apphost-pack-7.0-debuginfo?upstream=dotnet7.0",
    "dotnet7.0/dotnet-host": "pkg:rpm/redhat/dotnet-host?upstream=dotnet7.0",
    "dotnet7.0/dotnet-host-debuginfo": "pkg:rpm/redhat/dotnet-host-debuginfo?upstream=dotnet7.0",
    "dotnet7.0/dotnet-hostfxr-7.0": "pkg:rpm/redhat/dotnet-hostfxr-7.0?upstream=dotnet7.0",
    "dotnet7.0/dotnet-hostfxr-7.0-debuginfo": "pkg:rpm/redhat/dotnet-hostfxr-7.0-debuginfo?upstream=dotnet7.0",
    "dotnet7.0/dotnet-runtime-7.0": "pkg:rpm/redhat/dotnet-runtime-7.0?upstream=dotnet7.0",
    "dotnet7.0/dotnet-runtime-7.0-debuginfo": "pkg:rpm/redhat/dotnet-runtime-7.0-debuginfo?upstream=dotnet7.0",
    "dotnet7.0/dotnet-sdk-7.0": "pkg:rpm/redhat/dotnet-sdk-7.0?upstream=dotnet7.0",
    "dotnet7.0/dotnet-sdk-7.0-debuginfo": "pkg:rpm/redhat/dotnet-sdk-7.0-debuginfo?upstream=dotnet7.0",
    "dotnet7.0/dotnet-sdk-7.0-source-built-artifacts": "pkg:rpm/redhat/dotnet-sdk-7.0-source-built-artifacts?upstream=dotnet7.0",
    "dotnet7.0/dotnet-targeting-pack-7.0": "pkg:rpm/redhat/dotnet-targeting-pack-7.0?upstream=dotnet7.0",
    "dotnet7.0/dotnet-templates-7.0": "pkg:rpm/redhat/dotnet-templates-7.0?upstream=dotnet7.0",
    "dotnet7.0/dotnet7.0-debuginfo": "pkg:rpm/redhat/dotnet7.0-debuginfo?upstream=dotnet7.0",
    "dotnet7.0/dotnet7.0-debugsource": "pkg:rpm/redhat/dotnet7.0-debugsource?upstream=dotnet7.0",
    "dotnet7.0/netstandard-targeting-pack-2.1": "pkg:rpm/redhat/netstandard-targeting-pack-2.1?upstream=dotnet7.0",
    "dotnet8.0-0:8.0.121-1.el10_0.src": "pkg:rpm/redhat/dotnet8.0@8.0.121-1.el10_0?arch=src&epoch=0",
    "dotnet8.0-0:8.0.121-1.el8_10.src": "pkg:rpm/redhat/dotnet8.0@8.0.121-1.el8_10?arch=src&epoch=0",
    "dotnet8.0-0:8.0.121-1.el9_4.src": "pkg:rpm/redhat/dotnet8.0@8.0.121-1.el9_4?arch=src&epoch=0",
    "dotnet8.0-0:8.0.121-1.el9_6.src": "pkg:rpm/redhat/dotnet8.0@8.0.121-1.el9_6?arch=src&epoch=0",
    "dotnet8.0-0:8.0.126-1.hum1.src": "pkg:rpm/redhat/dotnet8.0@8.0.126-1.hum1?arch=src",
    "dotnet8.0.src": "pkg:rpm/redhat/dotnet8.0?arch=src",
    "dotnet8.0/aspnetcore-runtime-8.0": "pkg:rpm/redhat/aspnetcore-runtime-8.0?upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/aspnetcore-runtime-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/aspnetcore-runtime-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/aspnetcore-runtime-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/aspnetcore-runtime-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-dbg-8.0": "pkg:rpm/redhat/aspnetcore-runtime-dbg-8.0?upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-dbg-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/aspnetcore-runtime-dbg-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-dbg-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/aspnetcore-runtime-dbg-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-dbg-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/aspnetcore-runtime-dbg-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-runtime-dbg-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/aspnetcore-runtime-dbg-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-targeting-pack-8.0": "pkg:rpm/redhat/aspnetcore-targeting-pack-8.0?upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-targeting-pack-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/aspnetcore-targeting-pack-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-targeting-pack-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/aspnetcore-targeting-pack-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-targeting-pack-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/aspnetcore-targeting-pack-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/aspnetcore-targeting-pack-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/aspnetcore-targeting-pack-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet": "pkg:rpm/redhat/dotnet?upstream=dotnet8.0",
    "dotnet8.0/dotnet-apphost-pack-8.0": "pkg:rpm/redhat/dotnet-apphost-pack-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-apphost-pack-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/dotnet-apphost-pack-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-apphost-pack-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/dotnet-apphost-pack-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-apphost-pack-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/dotnet-apphost-pack-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-apphost-pack-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/dotnet-apphost-pack-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-apphost-pack-8.0-debuginfo": "pkg:rpm/redhat/dotnet-apphost-pack-8.0-debuginfo?upstream=dotnet8.0",
    "dotnet8.0/dotnet-host": "pkg:rpm/redhat/dotnet-host?upstream=dotnet8.0",
    "dotnet8.0/dotnet-host-0:8.0.21-1.el9_4": "pkg:rpm/redhat/dotnet-host@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-host-debuginfo": "pkg:rpm/redhat/dotnet-host-debuginfo?upstream=dotnet8.0",
    "dotnet8.0/dotnet-hostfxr-8.0": "pkg:rpm/redhat/dotnet-hostfxr-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-hostfxr-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/dotnet-hostfxr-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-hostfxr-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/dotnet-hostfxr-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-hostfxr-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/dotnet-hostfxr-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-hostfxr-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/dotnet-hostfxr-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-hostfxr-8.0-debuginfo": "pkg:rpm/redhat/dotnet-hostfxr-8.0-debuginfo?upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-8.0": "pkg:rpm/redhat/dotnet-runtime-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/dotnet-runtime-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/dotnet-runtime-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/dotnet-runtime-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/dotnet-runtime-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-8.0-debuginfo": "pkg:rpm/redhat/dotnet-runtime-8.0-debuginfo?upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-dbg-8.0": "pkg:rpm/redhat/dotnet-runtime-dbg-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-dbg-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/dotnet-runtime-dbg-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-dbg-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/dotnet-runtime-dbg-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-dbg-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/dotnet-runtime-dbg-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-runtime-dbg-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/dotnet-runtime-dbg-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0": "pkg:rpm/redhat/dotnet-sdk-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-0:8.0.121-1.el10_0": "pkg:rpm/redhat/dotnet-sdk-8.0@8.0.121-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-0:8.0.121-1.el8_10": "pkg:rpm/redhat/dotnet-sdk-8.0@8.0.121-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-0:8.0.121-1.el9_4": "pkg:rpm/redhat/dotnet-sdk-8.0@8.0.121-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-0:8.0.121-1.el9_6": "pkg:rpm/redhat/dotnet-sdk-8.0@8.0.121-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-debuginfo": "pkg:rpm/redhat/dotnet-sdk-8.0-debuginfo?upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-source-built-artifacts": "pkg:rpm/redhat/dotnet-sdk-8.0-source-built-artifacts?upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-source-built-artifacts-0:8.0.121-1.el10_0":
        "pkg:rpm/redhat/dotnet-sdk-8.0-source-built-artifacts@8.0.121-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-source-built-artifacts-0:8.0.121-1.el8_10":
        "pkg:rpm/redhat/dotnet-sdk-8.0-source-built-artifacts@8.0.121-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-source-built-artifacts-0:8.0.121-1.el9_4":
        "pkg:rpm/redhat/dotnet-sdk-8.0-source-built-artifacts@8.0.121-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-8.0-source-built-artifacts-0:8.0.121-1.el9_6":
        "pkg:rpm/redhat/dotnet-sdk-8.0-source-built-artifacts@8.0.121-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-dbg-8.0": "pkg:rpm/redhat/dotnet-sdk-dbg-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-dbg-8.0-0:8.0.121-1.el10_0": "pkg:rpm/redhat/dotnet-sdk-dbg-8.0@8.0.121-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-dbg-8.0-0:8.0.121-1.el8_10": "pkg:rpm/redhat/dotnet-sdk-dbg-8.0@8.0.121-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-dbg-8.0-0:8.0.121-1.el9_4": "pkg:rpm/redhat/dotnet-sdk-dbg-8.0@8.0.121-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-sdk-dbg-8.0-0:8.0.121-1.el9_6": "pkg:rpm/redhat/dotnet-sdk-dbg-8.0@8.0.121-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-targeting-pack-8.0": "pkg:rpm/redhat/dotnet-targeting-pack-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-targeting-pack-8.0-0:8.0.21-1.el10_0": "pkg:rpm/redhat/dotnet-targeting-pack-8.0@8.0.21-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-targeting-pack-8.0-0:8.0.21-1.el8_10": "pkg:rpm/redhat/dotnet-targeting-pack-8.0@8.0.21-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-targeting-pack-8.0-0:8.0.21-1.el9_4": "pkg:rpm/redhat/dotnet-targeting-pack-8.0@8.0.21-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-targeting-pack-8.0-0:8.0.21-1.el9_6": "pkg:rpm/redhat/dotnet-targeting-pack-8.0@8.0.21-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-templates-8.0": "pkg:rpm/redhat/dotnet-templates-8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet-templates-8.0-0:8.0.121-1.el10_0": "pkg:rpm/redhat/dotnet-templates-8.0@8.0.121-1.el10_0?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-templates-8.0-0:8.0.121-1.el8_10": "pkg:rpm/redhat/dotnet-templates-8.0@8.0.121-1.el8_10?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-templates-8.0-0:8.0.121-1.el9_4": "pkg:rpm/redhat/dotnet-templates-8.0@8.0.121-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet-templates-8.0-0:8.0.121-1.el9_6": "pkg:rpm/redhat/dotnet-templates-8.0@8.0.121-1.el9_6?epoch=0&upstream=dotnet8.0",
    "dotnet8.0/dotnet8.0": "pkg:rpm/redhat/dotnet8.0?upstream=dotnet8.0",
    "dotnet8.0/dotnet8.0-debuginfo": "pkg:rpm/redhat/dotnet8.0-debuginfo?upstream=dotnet8.0",
    "dotnet8.0/dotnet8.0-debugsource": "pkg:rpm/redhat/dotnet8.0-debugsource?upstream=dotnet8.0",
    "dotnet8.0/netstandard-targeting-pack-2.1": "pkg:rpm/redhat/netstandard-targeting-pack-2.1?upstream=dotnet8.0",
    "dotnet8.0/netstandard-targeting-pack-2.1-0:8.0.121-1.el9_4": "pkg:rpm/redhat/netstandard-targeting-pack-2.1@8.0.121-1.el9_4?epoch=0&upstream=dotnet8.0",
    "dotnet9.0-0:9.0.111-1.el10_0.src": "pkg:rpm/redhat/dotnet9.0@9.0.111-1.el10_0?arch=src&epoch=0",
    "dotnet9.0-0:9.0.111-1.el8_10.src": "pkg:rpm/redhat/dotnet9.0@9.0.111-1.el8_10?arch=src&epoch=0",
    "dotnet9.0-0:9.0.111-1.el9_6.src": "pkg:rpm/redhat/dotnet9.0@9.0.111-1.el9_6?arch=src&epoch=0",
    "dotnet9.0-0:9.0.116-1.hum1.src": "pkg:rpm/redhat/dotnet9.0@9.0.116-1.hum1?arch=src",
    "dotnet9.0.src": "pkg:rpm/redhat/dotnet9.0?arch=src",
    "dotnet9.0/aspnetcore-runtime-9.0": "pkg:rpm/redhat/aspnetcore-runtime-9.0?upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-runtime-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/aspnetcore-runtime-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-runtime-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/aspnetcore-runtime-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-runtime-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/aspnetcore-runtime-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-runtime-dbg-9.0": "pkg:rpm/redhat/aspnetcore-runtime-dbg-9.0?upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-runtime-dbg-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/aspnetcore-runtime-dbg-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-runtime-dbg-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/aspnetcore-runtime-dbg-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-runtime-dbg-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/aspnetcore-runtime-dbg-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-targeting-pack-9.0": "pkg:rpm/redhat/aspnetcore-targeting-pack-9.0?upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-targeting-pack-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/aspnetcore-targeting-pack-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-targeting-pack-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/aspnetcore-targeting-pack-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/aspnetcore-targeting-pack-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/aspnetcore-targeting-pack-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet": "pkg:rpm/redhat/dotnet?upstream=dotnet9.0",
    "dotnet9.0/dotnet-0:9.0.111-1.el8_10": "pkg:rpm/redhat/dotnet@9.0.111-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-apphost-pack-9.0": "pkg:rpm/redhat/dotnet-apphost-pack-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-apphost-pack-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/dotnet-apphost-pack-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-apphost-pack-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/dotnet-apphost-pack-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-apphost-pack-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/dotnet-apphost-pack-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-apphost-pack-9.0-debuginfo": "pkg:rpm/redhat/dotnet-apphost-pack-9.0-debuginfo?upstream=dotnet9.0",
    "dotnet9.0/dotnet-host": "pkg:rpm/redhat/dotnet-host?upstream=dotnet9.0",
    "dotnet9.0/dotnet-host-0:9.0.10-1.el10_0": "pkg:rpm/redhat/dotnet-host@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-host-0:9.0.10-1.el8_10": "pkg:rpm/redhat/dotnet-host@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-host-0:9.0.10-1.el9_6": "pkg:rpm/redhat/dotnet-host@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-host-debuginfo": "pkg:rpm/redhat/dotnet-host-debuginfo?upstream=dotnet9.0",
    "dotnet9.0/dotnet-hostfxr-9.0": "pkg:rpm/redhat/dotnet-hostfxr-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-hostfxr-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/dotnet-hostfxr-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-hostfxr-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/dotnet-hostfxr-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-hostfxr-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/dotnet-hostfxr-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-hostfxr-9.0-debuginfo": "pkg:rpm/redhat/dotnet-hostfxr-9.0-debuginfo?upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-9.0": "pkg:rpm/redhat/dotnet-runtime-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/dotnet-runtime-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/dotnet-runtime-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/dotnet-runtime-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-9.0-debuginfo": "pkg:rpm/redhat/dotnet-runtime-9.0-debuginfo?upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-dbg-9.0": "pkg:rpm/redhat/dotnet-runtime-dbg-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-dbg-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/dotnet-runtime-dbg-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-dbg-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/dotnet-runtime-dbg-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-runtime-dbg-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/dotnet-runtime-dbg-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0": "pkg:rpm/redhat/dotnet-sdk-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-0:9.0.111-1.el10_0": "pkg:rpm/redhat/dotnet-sdk-9.0@9.0.111-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-0:9.0.111-1.el8_10": "pkg:rpm/redhat/dotnet-sdk-9.0@9.0.111-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-0:9.0.111-1.el9_6": "pkg:rpm/redhat/dotnet-sdk-9.0@9.0.111-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-debuginfo": "pkg:rpm/redhat/dotnet-sdk-9.0-debuginfo?upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-source-built-artifacts": "pkg:rpm/redhat/dotnet-sdk-9.0-source-built-artifacts?upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-source-built-artifacts-0:9.0.111-1.el10_0":
        "pkg:rpm/redhat/dotnet-sdk-9.0-source-built-artifacts@9.0.111-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-source-built-artifacts-0:9.0.111-1.el8_10":
        "pkg:rpm/redhat/dotnet-sdk-9.0-source-built-artifacts@9.0.111-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-9.0-source-built-artifacts-0:9.0.111-1.el9_6":
        "pkg:rpm/redhat/dotnet-sdk-9.0-source-built-artifacts@9.0.111-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-aot-9.0": "pkg:rpm/redhat/dotnet-sdk-aot-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-aot-9.0-0:9.0.111-1.el10_0": "pkg:rpm/redhat/dotnet-sdk-aot-9.0@9.0.111-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-aot-9.0-0:9.0.111-1.el8_10": "pkg:rpm/redhat/dotnet-sdk-aot-9.0@9.0.111-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-aot-9.0-0:9.0.111-1.el9_6": "pkg:rpm/redhat/dotnet-sdk-aot-9.0@9.0.111-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-aot-9.0-debuginfo": "pkg:rpm/redhat/dotnet-sdk-aot-9.0-debuginfo?upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-dbg-9.0": "pkg:rpm/redhat/dotnet-sdk-dbg-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-dbg-9.0-0:9.0.111-1.el10_0": "pkg:rpm/redhat/dotnet-sdk-dbg-9.0@9.0.111-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-dbg-9.0-0:9.0.111-1.el8_10": "pkg:rpm/redhat/dotnet-sdk-dbg-9.0@9.0.111-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-sdk-dbg-9.0-0:9.0.111-1.el9_6": "pkg:rpm/redhat/dotnet-sdk-dbg-9.0@9.0.111-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-targeting-pack-9.0": "pkg:rpm/redhat/dotnet-targeting-pack-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-targeting-pack-9.0-0:9.0.10-1.el10_0": "pkg:rpm/redhat/dotnet-targeting-pack-9.0@9.0.10-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-targeting-pack-9.0-0:9.0.10-1.el8_10": "pkg:rpm/redhat/dotnet-targeting-pack-9.0@9.0.10-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-targeting-pack-9.0-0:9.0.10-1.el9_6": "pkg:rpm/redhat/dotnet-targeting-pack-9.0@9.0.10-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-templates-9.0": "pkg:rpm/redhat/dotnet-templates-9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet-templates-9.0-0:9.0.111-1.el10_0": "pkg:rpm/redhat/dotnet-templates-9.0@9.0.111-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-templates-9.0-0:9.0.111-1.el8_10": "pkg:rpm/redhat/dotnet-templates-9.0@9.0.111-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet-templates-9.0-0:9.0.111-1.el9_6": "pkg:rpm/redhat/dotnet-templates-9.0@9.0.111-1.el9_6?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/dotnet9.0": "pkg:rpm/redhat/dotnet9.0?upstream=dotnet9.0",
    "dotnet9.0/dotnet9.0-debuginfo": "pkg:rpm/redhat/dotnet9.0-debuginfo?upstream=dotnet9.0",
    "dotnet9.0/dotnet9.0-debugsource": "pkg:rpm/redhat/dotnet9.0-debugsource?upstream=dotnet9.0",
    "dotnet9.0/netstandard-targeting-pack-2.1": "pkg:rpm/redhat/netstandard-targeting-pack-2.1?upstream=dotnet9.0",
    "dotnet9.0/netstandard-targeting-pack-2.1-0:9.0.111-1.el10_0": "pkg:rpm/redhat/netstandard-targeting-pack-2.1@9.0.111-1.el10_0?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/netstandard-targeting-pack-2.1-0:9.0.111-1.el8_10": "pkg:rpm/redhat/netstandard-targeting-pack-2.1@9.0.111-1.el8_10?epoch=0&upstream=dotnet9.0",
    "dotnet9.0/netstandard-targeting-pack-2.1-0:9.0.111-1.el9_6": "pkg:rpm/redhat/netstandard-targeting-pack-2.1@9.0.111-1.el9_6?epoch=0&upstream=dotnet9.0",
}

# Add decoded keys (e.g. %2B → +) to match what _parse_branches() does at runtime
PACKAGE_PURL.update({unquote(k): v for k, v in PACKAGE_PURL.items() if k != unquote(k)})


@pytest.fixture
def ctrl() -> VexFeedController:
    """VexFeedController without database connection."""
    with patch.object(VexFeedController, "__init__", lambda self: None):
        controller = VexFeedController()
    controller.logger = MagicMock()
    controller.cfg = MagicMock()
    controller.cfg.csaf_product_status_list = ["fixed", "known_affected"]
    controller.tmp_directory = pathlib.Path("/tmp")
    return controller


# ===================================================================
# Fixed products
# ===================================================================


class TestFixedSrpmNoLineage:
    """fixed | SRPM (.src) | no lineage | '+' unencoded"""

    PRODUCT = "rhel-8.8.0.z.eus::appstream:nodejs-0:16.20.2-4.module+el8.8.0+21546+ecd4bb56.src"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8.8.0.z.eus::appstream"
        assert pkg == "nodejs-0:16.20.2-4.module+el8.8.0+21546+ecd4bb56.src"
        assert module is None
        assert variant == "8.8.0.z.eus"


class TestFixedBinaryLineageEncoded:
    """fixed | lineage 'nodejs/' | binary RPM | %2B-encoded | no arch in input"""

    PRODUCT = "rhel-8.8.0.z.eus::appstream:nodejs/nodejs-0:16.20.2-4.module%2Bel8.8.0%2B21546%2Becd4bb56"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8.8.0.z.eus::appstream"
        assert pkg == "nodejs-0:16.20.2-4.module+el8.8.0+21546+ecd4bb56.x86_64"
        assert module is None
        assert variant == "8.8.0.z.eus"


class TestFixedLineageEpoch1:
    """fixed | lineage | epoch=1 | non-modular (el9_2) | no .src → .x86_64"""

    PRODUCT = "rhel-9.2.0.z.eus::appstream:nodejs/nodejs-1:16.20.2-4.el9_2"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-9.2.0.z.eus::appstream"
        assert pkg == "nodejs-1:16.20.2-4.el9_2.x86_64"
        assert module is None
        assert variant == "9.2.0.z.eus"


class TestFixedLineageDifferentName:
    """fixed | lineage name ≠ package name (nodejs/npm) | branch without .eus"""

    PRODUCT = "rhel-9.3.0.z::appstream:nodejs/npm-1:8.19.4-1.16.20.2.4.el9_3"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-9.3.0.z::appstream"
        assert pkg == "npm-1:8.19.4-1.16.20.2.4.el9_3.x86_64"
        assert module is None
        assert variant == "9.3.0.z"


class TestFixedNsvcaDoubleSlash:
    """fixed | NSVCA module path with 2 slashes | BUG: needs rsplit('/', 1)

    Input:  rhel-8.9.0.z::appstream:nodejs:16:…/nodejs/nodejs-0:16.20.2-4.module+…
    The component has TWO '/': module_nsvca/lineage/pkg-NEVRA
    split('/', 1) wrongly splits at the first '/' leaving 'nodejs/nodejs-0:…' as pkg.
    rsplit('/', 1) correctly yields 'nodejs-0:16.20.2-4.module+…' as pkg.
    """

    PRODUCT = (
        "rhel-8.9.0.z::appstream:"
        "nodejs:16:8090020240315081818:a75119d5/nodejs/"
        "nodejs-0:16.20.2-4.module%2Bel8.9.0%2B21536%2B8fdee1fb"
    )

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8.9.0.z::appstream"
        assert pkg == "nodejs-0:16.20.2-4.module+el8.9.0+21536+8fdee1fb.x86_64"
        assert module is None
        assert variant == "8.9.0.z"


class TestFixedBrPrefix:
    """fixed | rhel-br- prefix | SRPM | BUG: variant_suffix includes 'br-'

    _extract_variant_suffix('rhel-br-8.6.0.z.eus::appstream') uses split('-', 1)
    which yields 'br-8.6.0.z.eus' instead of '8.6.0.z.eus'.
    'rhel-br' is a distinct product prefix (Build Root), not a version component.
    """

    PRODUCT = "rhel-br-8.6.0.z.eus::appstream:nodejs-0:16.20.2-4.module+el8.6.0+21547+94389150.src"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-br-8.6.0.z.eus::appstream"
        assert pkg == "nodejs-0:16.20.2-4.module+el8.6.0+21547+94389150.src"
        assert module is None
        assert variant == "8.6.0.z.eus"


class TestFixedRhsclSrpm:
    """fixed | rhscl prefix | ::el7 channel | SRPM"""

    PRODUCT = "rhscl-3.8.0::el7:rh-nodejs14-nodejs-0:14.21.3-6.el7.src"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhscl-3.8.0::el7"
        assert pkg == "rh-nodejs14-nodejs-0:14.21.3-6.el7.src"
        assert module is None
        assert variant == "3.8.0"


class TestFixedRhsclLineage:
    """fixed | rhscl + lineage (lineage == base package name) | binary RPM"""

    PRODUCT = "rhscl-3.8.0::el7:rh-nodejs14-nodejs/rh-nodejs14-nodejs-0:14.21.3-6.el7"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhscl-3.8.0::el7"
        assert pkg == "rh-nodejs14-nodejs-0:14.21.3-6.el7.x86_64"
        assert module is None
        assert variant == "3.8.0"


# ===================================================================
# Known-affected products
# ===================================================================


class TestKnownAffectedModuleNsvca:
    """known_affected | module NSVCA without channel (':' not '::') | trailing /pkg"""

    PRODUCT = "rhel-8.10.0:nodejs:16:8090020240315081818:a75119d5/nodejs"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8.10.0"
        assert pkg == "nodejs"
        assert module == "nodejs:16"
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedModuleRhel9Context:
    """known_affected | module context='rhel9' (not hash) | branch rhel-9.3.0.z"""

    PRODUCT = "rhel-9.3.0.z:nodejs:18:9030020240301111035:rhel9/nodejs"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-9.3.0.z"
        assert pkg == "nodejs"
        assert module == "nodejs:18"
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedContainer:
    """known_affected | non-rhel prefix | OCI container (odf4/…) | lineage"""

    PRODUCT = "openshift-data-foundation-4.12.z:odf4/mcg-core-rhel8"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "openshift-data-foundation-4.12.z"
        assert pkg == "mcg-core-rhel8"
        assert module is None
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedBareBranchSrc:
    """known_affected | bare branch 'rhel-8' | .src name-only | no '/'"""

    PRODUCT = "rhel-8:vim.src"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8"
        assert pkg == "vim.src"
        assert module is None
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedLineageNameOnly:
    """known_affected | lineage name-only (no NEVRA, no arch) | e.g. vim/vim-common"""

    PRODUCT = "rhel-9:vim/vim-common"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-9"
        assert pkg == "vim-common"
        assert module is None
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedElsLifecycle:
    """known_affected | dotted lifecycle '.els' | branch 'rhel-7.els'"""

    PRODUCT = "rhel-7.els:vim/vim-enhanced"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-7.els"
        assert pkg == "vim-enhanced"
        assert module is None
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedMultiDashEls:
    """known_affected | multi-dash + dotted 'rhel-6-els.els' | .src"""

    PRODUCT = "rhel-6-els.els:vim.src"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-6-els.els"
        assert pkg == "vim.src"
        assert module is None
        assert variant == DEFAULT_VARIANT


# ===================================================================
# Fixed products — from CVE-2024-0646 / CVE-2024-21626
# ===================================================================


class TestFixedContainerNevra:
    """fixed | OCI container with -v<ver> in name | non-rhel prefix | no lineage slash"""

    PRODUCT = "openshift-logging-5.8::el9:cluster-logging-operator-container-v5.8.6-0:11"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "openshift-logging-5.8::el9"
        assert pkg == "cluster-logging-operator-container-v5.8.6-0:11.x86_64"
        assert module is None
        assert variant == "5.8"


class TestFixedModulePathDoubleSlash:
    """fixed | module-like path container-tools:rhel8/buildah/buildah | 2 slashes in component"""

    PRODUCT = "rhel-8.4.0.z.aus::appstream:container-tools:rhel8/buildah/buildah"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8.4.0.z.aus::appstream"
        assert pkg == "buildah.x86_64"
        assert module is None
        assert variant == "8.4.0.z.aus"


# ===================================================================
# Known-affected products — from CVE-2024-0646 / CVE-2024-21626
# ===================================================================


class TestKnownAffectedModuleDoubleSlash:
    """known_affected | module container-tools:4.0 | double slash (module/lineage/pkg)"""

    PRODUCT = "rhel-8.2.0.z.aus:container-tools:4.0/runc/runc"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8.2.0.z.aus"
        assert pkg == "runc"
        assert module == "container-tools:4.0"
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedModuleSrc:
    """known_affected | module container-tools:4.0 + .src pkg after single /"""

    PRODUCT = "rhel-8.10.0:container-tools:4.0/runc.src"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-8.10.0"
        assert pkg == "runc.src"
        assert module == "container-tools:4.0"
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedBarePackageNoSrc:
    """known_affected | bare package name without .src and without / | OCI container"""

    PRODUCT = "rhpm-0.1:kepler-container"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhpm-0.1"
        assert pkg == "kepler-container"
        assert module is None
        assert variant == DEFAULT_VARIANT


class TestKnownAffectedFullNevra:
    """known_affected | lineage + full NEVRA with epoch=2 (docker/docker-2:1.13.1-...)"""

    PRODUCT = "rhel-7.9.z:docker/docker-2:1.13.1-210.git7d71120.el7_9"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "known_affected", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-7.9.z"
        assert pkg == "docker-2:1.13.1-210.git7d71120.el7_9"
        assert module is None
        assert variant == DEFAULT_VARIANT


# ===================================================================
# Fixed products — from CVE-2025-55315
# ===================================================================


class TestFixedNoChannelTildeVersion:
    """fixed | single ':' (no ::channel) | tilde '~' in version (pre-release RPM) | lineage"""

    PRODUCT = "rhel-10.1:dotnet10.0/dotnet-host-0:10.0.0~rc.2.25502.107-0.12.el10_1"

    def test_parse(self, ctrl: VexFeedController) -> None:
        branch, pkg, module, variant = ctrl._parse_product(self.PRODUCT, "fixed", PRODUCT_CPE, PACKAGE_PURL)
        assert branch == "rhel-10.1"
        assert pkg == "dotnet-host-0:10.0.0~rc.2.25502.107-0.12.el10_1.x86_64"
        assert module is None
        assert variant == "10.1"
