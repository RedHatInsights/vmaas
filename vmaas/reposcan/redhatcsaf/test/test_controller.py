"""Unit tests of csaf_controller.py."""
import pathlib
from datetime import datetime
import pytest


from vmaas.reposcan.redhatcsaf.csaf_controller import CsafController
from vmaas.reposcan.redhatcsaf.modeling import CsafCves, CsafData, CsafFiles
from vmaas.reposcan.redhatcsaf.modeling import CsafFile
from vmaas.reposcan.redhatcsaf.modeling import CsafProduct


EXPECTED_PARSE = (
    ("cve-2023-0030.json", CsafCves({"CVE-2023-0030": []})),
    (
        "cve-2023-0049.json",
        CsafCves(
            {
                "CVE-2023-0049": [
                    CsafProduct("cpe:/o:redhat:enterprise_linux:6", "vim", 4),
                    CsafProduct("cpe:/o:redhat:enterprise_linux:7", "vim", 4),
                    CsafProduct("cpe:/o:redhat:enterprise_linux:8", "vim", 4),
                    CsafProduct("cpe:/o:redhat:enterprise_linux:9", "vim", 4),
                ]
            }
        ),
    ),
    (
        "cve-2023-1017.json",
        CsafCves(
            {
                "CVE-2023-1017": [
                    CsafProduct("cpe:/o:redhat:enterprise_linux:8", "libtpms", 4, "virt:rhel"),
                    CsafProduct("cpe:/a:redhat:advanced_virtualization:8::el8", "libtpms", 4, "virt:8.2"),
                    CsafProduct("cpe:/a:redhat:advanced_virtualization:8::el8", "libtpms", 4, "virt:8.3"),
                    CsafProduct("cpe:/a:redhat:advanced_virtualization:8::el8", "libtpms", 4, "virt:av"),
                ]
            }
        ),
    ),
)


class TestCsafController:
    """CsafController tests."""

    @pytest.fixture
    def csaf(self, db_conn):  # pylint: disable=unused-argument
        """Fixture returning CsafController obj with tmp_directory se to current directory."""
        csaf = CsafController()
        csaf.tmp_directory = pathlib.Path(__file__).parent.resolve()
        return csaf

    @pytest.mark.parametrize("data", EXPECTED_PARSE, ids=[x[0] for x in EXPECTED_PARSE])
    def test_parse_csaf_file(self, data, csaf):
        """Test CSAF JSON file parsing."""
        csaf_json, expected = data
        csaf_file = CsafFile(csaf_json, None)
        parsed = csaf.parse_csaf_file(csaf_file)
        assert parsed == expected

    @pytest.mark.parametrize("data", EXPECTED_PARSE, ids=[x[0] for x in EXPECTED_PARSE])
    def test_csaf_store(self, data, csaf: CsafController):
        """Parse CSAF JSON and store its data to DB"""
        csaf_json, _ = data
        csaf_file = CsafFile(csaf_json, datetime(2022, 2, 14, 15, 30))
        csaf_cves = csaf.parse_csaf_file(csaf_file)
        csaf_data = CsafData(CsafFiles({csaf_json: csaf_file}), csaf_cves)
        csaf.csaf_store.store(csaf_data)
