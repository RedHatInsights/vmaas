"""CSAF signature verification unit tests using local fixtures."""
# pylint: disable=missing-function-docstring,protected-access,invalid-name
from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from vmaas.reposcan.redhatcsaf.csaf_controller import CSAF_VEX_PUB_SIG_KEY_FILE
from vmaas.reposcan.redhatcsaf.csaf_controller import CSAF_VEX_SIGNATURE_FILE_SUFFIX
from vmaas.reposcan.redhatcsaf.csaf_controller import CsafController

TEST_DIR = Path(__file__).resolve().parent
WRONG_PUBLIC_KEY = TEST_DIR / "fd431d51.txt"

VALID_JSON = TEST_DIR / "cve-2026-0006.json"
VALID_SIGNATURE = TEST_DIR / "cve-2026-0006.json.asc"
# Repo copy of cve-2023-0030.json and .asc are not a matching download pair
MISMATCHED_JSON = TEST_DIR / "cve-2023-0030.json"

pytest.importorskip("gnupg")
requires_gpg = pytest.mark.skipif(shutil.which("gpg") is None, reason="gpg binary required")
requires_pub_key = pytest.mark.skipif(
    not CSAF_VEX_PUB_SIG_KEY_FILE.is_file(),
    reason=f"CSAF public key missing at {CSAF_VEX_PUB_SIG_KEY_FILE}",
)


@pytest.fixture(name="csaf")
def csaf_fixture(tmp_path: Path) -> CsafController:
    with patch("vmaas.reposcan.redhatcsaf.csaf_controller.CsafStore"):
        controller = CsafController()
    controller.tmp_directory = tmp_path
    return controller


def _copy_with_signature(tmp_path: Path, json_src: Path, signature_src: Path) -> Path:
    """Copy JSON and detached signature so both sit next to each other in tmp_path"""
    target_json = tmp_path / json_src.name
    shutil.copy(json_src, target_json)
    shutil.copy(signature_src, Path(str(target_json) + CSAF_VEX_SIGNATURE_FILE_SUFFIX))
    return target_json


@requires_gpg
class TestVerifyCsafFileSignature:
    """Offline tests for _verify_csaf_signature using test fixtures"""

    def test_signature_verifier_is_available(self, csaf: CsafController) -> None:
        assert csaf._get_signature_verifier() is not None

    def test_verify_valid_signed_json(self, csaf: CsafController) -> None:
        assert csaf._verify_csaf_signature(VALID_JSON) is True

    def test_verify_mismatched_signature(self, csaf: CsafController) -> None:
        assert csaf._verify_csaf_signature(MISMATCHED_JSON) is False

    def test_verify_wrong_public_key(self, tmp_path: Path) -> None:
        file_path = _copy_with_signature(tmp_path, VALID_JSON, VALID_SIGNATURE)
        with patch("vmaas.reposcan.redhatcsaf.csaf_controller.CsafStore"):
            with patch("vmaas.reposcan.redhatcsaf.csaf_controller.CSAF_VEX_PUB_SIG_KEY_FILE", WRONG_PUBLIC_KEY):
                csaf = CsafController()
                assert csaf._verify_csaf_signature(file_path) is False

    def test_verify_missing_signature_file(self, csaf: CsafController, tmp_path: Path) -> None:
        file_path = tmp_path / VALID_JSON.name
        shutil.copy(VALID_JSON, file_path)
        assert csaf._verify_csaf_signature(file_path) is False

    def test_missing_public_key_at_init(self, tmp_path: Path) -> None:
        missing_key = tmp_path / "missing-pub.key"
        with patch("vmaas.reposcan.redhatcsaf.csaf_controller.CsafStore"):
            with patch("vmaas.reposcan.redhatcsaf.csaf_controller.CSAF_VEX_PUB_SIG_KEY_FILE", missing_key):
                csaf = CsafController()
                assert csaf._get_signature_verifier() is None
                assert csaf._verify_csaf_signature(VALID_JSON) is False

    @patch("vmaas.reposcan.redhatcsaf.csaf_controller.CSAF_VEX_SIGNATURE_VERIFY", False)
    def test_verify_bypasses_when_disabled(self, csaf: CsafController) -> None:
        assert csaf._verify_csaf_signature(VALID_JSON) is True

    @patch("vmaas.reposcan.redhatcsaf.csaf_controller.CSAF_VEX_SIGNATURE_VERIFY", False)
    def test_queue_skips_signature_when_disabled(self, csaf: CsafController) -> None:
        with patch.object(csaf.downloader, "add") as mock_add:
            file_item, signature_item = csaf._queue_download_csaf_payload_and_signature("cve/foo.json")
        assert signature_item is None
        assert mock_add.call_count == 1
        assert file_item.target_path == csaf.tmp_directory / "cve/foo.json"
