"""
GPG signature verification
"""

from pathlib import Path

from pysequoia import Cert, Sig, verify

from vmaas.common.logging_utils import get_logger


class GpgSignatureVerifierError(Exception):
    """Failed to initialize GPG signature verifier"""


class GpgSignatureVerifier:
    """Verify GPG signatures using imported public key(s)"""

    def __init__(self, public_key_file: Path) -> None:
        self.logger = get_logger(__name__)
        self.public_key_file = public_key_file
        if not public_key_file.is_file():
            self.logger.error("GPG public key not found at %s", public_key_file)
            raise GpgSignatureVerifierError("public key file not found")

        self._certs = {}
        self._import_public_key(public_key_file)

    def verify(self, data_file: Path, signature_file: Path) -> bool:
        """Return True when signature_file is a valid signature for data_file"""
        if not signature_file.is_file():
            self.logger.error("Signature file not found at %s", signature_file)
            return False

        self.logger.debug(
            "Verifying signature for %s against %s using %s.",
            data_file, signature_file, self.public_key_file,
        )

        try:
            signature = Sig.from_file(str(signature_file))

            def cert_store(_key_ids):
                # Return all loaded certificates, library will pick the correct one
                return list(self._certs.values())

            result = verify(file=str(data_file), store=cert_store, signature=signature)

            if result.valid_sigs:  # Means, there is at least one valid signature
                self.logger.debug("Signature for %s is valid.", data_file)
                self.logger.debug("Signed by: %s", result.valid_sigs[0].certificate)
                return True

            self.logger.error("Signature for %s is invalid or corrupted.", data_file)
            return False

        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.error("Failed to verify signature for %s: %s", data_file, err)
            return False

    def _import_public_key(self, public_key_file: Path) -> None:
        """Import all public key certificates from the cert file"""
        try:
            # Parse all certificates found inside the file
            for cert in Cert.split_file(str(public_key_file)):
                self._certs[cert.fingerprint] = cert
                self.logger.debug("Successfully imported certificate with fingerprint: %s", cert.fingerprint)

            if not self._certs:
                raise GpgSignatureVerifierError("No valid certificates found in file")

        except Exception as err:  # pylint: disable=broad-exception-caught
            self.logger.error("Failed to import GPG public keys from %s: %s", public_key_file, err)
            raise GpgSignatureVerifierError("failed to import public keys") from err
