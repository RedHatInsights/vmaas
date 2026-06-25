"""
GPG signature verification
"""

import shutil
import tempfile
from pathlib import Path

import gnupg

from vmaas.common.logging_utils import get_logger


class GpgSignatureVerifierError(Exception):
    """Failed to initialize GPG signature verifier"""


class GpgSignatureVerifier:
    """Verify GPG signatures using a single imported public key"""

    def __init__(self, public_key_file: Path) -> None:
        self.logger = get_logger(__name__)
        self.public_key_file = public_key_file
        if not public_key_file.is_file():
            self.logger.error("GPG public key not found at %s", public_key_file)
            raise GpgSignatureVerifierError("public key file not found")
        self._gpg_home = tempfile.mkdtemp(prefix="gpg-")
        self._gpg = gnupg.GPG(gnupghome=self._gpg_home)
        try:
            self._import_public_key(public_key_file)
        except GpgSignatureVerifierError:
            self.close()
            raise

    def close(self) -> None:
        """Remove the temporary GPG home directory."""
        gpg_home = getattr(self, "_gpg_home", None)
        if gpg_home is not None:
            shutil.rmtree(gpg_home, ignore_errors=True)
            self._gpg_home = None

    def __del__(self) -> None:
        self.close()

    def verify(self, data_file: Path, signature_file: Path) -> bool:
        """Return True when signature_file is a valid signature for data_file"""
        if not signature_file.is_file():
            self.logger.error("Signature file not found at %s", signature_file)
            return False

        self.logger.debug(
            "Verifying signature for %s against %s using %s.",
            data_file, signature_file, self.public_key_file,
        )
        with open(signature_file, "rb") as sig_f:
            verified = self._gpg.verify_file(sig_f, data_filename=str(data_file))

        if verified:
            self.logger.debug("Signature for %s is valid.", data_file)
            self.logger.debug("Signed by: %s", verified.username)
            return True

        self.logger.error("Signature for %s is invalid or corrupted.", data_file)
        return False

    def _import_public_key(self, public_key_file: Path) -> None:
        with open(public_key_file, encoding="utf-8") as key_file:
            import_result = self._gpg.import_keys(key_file.read())
        if import_result.count == 0:
            self.logger.error("Failed to import GPG public key from %s", public_key_file)
            raise GpgSignatureVerifierError("failed to import public key")
