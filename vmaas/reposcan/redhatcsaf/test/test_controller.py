"""Unit tests of csaf_controller.py."""
import pathlib
from datetime import datetime

import pytest

from vmaas.reposcan.conftest import EXPECTED_CSAF
from vmaas.reposcan.redhatcsaf.csaf_controller import CsafController
from vmaas.reposcan.redhatcsaf.modeling import CsafData
from vmaas.reposcan.redhatcsaf.modeling import CsafFile
from vmaas.reposcan.redhatcsaf.modeling import CsafFiles


class TestCsafController:
    """CsafController tests."""

    @pytest.fixture
    def csaf(self, db_conn):  # pylint: disable=unused-argument
        """Fixture returning CsafController obj with tmp_directory se to current directory."""
        csaf = CsafController()
        csaf.tmp_directory = pathlib.Path(__file__).parent.resolve()
        return csaf

    @pytest.mark.parametrize("data", EXPECTED_CSAF, ids=[x[0] for x in EXPECTED_CSAF])
    def test_parse_csaf_file(self, data, csaf):
        """Test CSAF JSON file parsing."""
        csaf_json, expected = data
        csaf_file = CsafFile(csaf_json, None)
        parsed = csaf.parse_csaf_file(csaf_file)
        assert parsed == expected

    @pytest.mark.parametrize("data", EXPECTED_CSAF, ids=[x[0] for x in EXPECTED_CSAF])
    def test_csaf_store(self, data, csaf: CsafController):
        """Parse CSAF JSON and store its data to DB"""
        csaf_json, _ = data
        csaf_file = CsafFile(csaf_json, datetime(2022, 2, 14, 15, 30))
        csaf_cves = csaf.parse_csaf_file(csaf_file)
        csaf_data = CsafData(CsafFiles({csaf_json: csaf_file}), csaf_cves)
        csaf.csaf_store.store(csaf_data)
