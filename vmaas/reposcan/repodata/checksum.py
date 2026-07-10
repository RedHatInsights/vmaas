"""
Module for verifying checksums of downloaded files.
"""
import hashlib


class ChecksumError(Exception):
    """Raised when checksum verification fails."""


def verify_file_checksum(file_path, expected_checksum, checksum_type):
    """
    Verify that a file's checksum matches the expected value.

    Args:
        file_path: Path to the file to verify
        expected_checksum: Expected checksum value (hex string)
        checksum_type: Type of checksum (e.g., 'sha256', 'sha512')
    """

    # Map common checksum type names to hashlib algorithm names
    checksum_type = checksum_type.lower()

    # Compute the file's checksum
    try:
        hasher = hashlib.new(checksum_type)
    except ValueError as exc:
        raise ValueError(f"Unsupported checksum type: {checksum_type}") from exc
    with open(file_path, 'rb') as file_handle:
        while True:
            chunk = file_handle.read(65536)  # 64KB chunks
            if not chunk:
                break
            hasher.update(chunk)

    computed_checksum = hasher.hexdigest()

    # Compare checksums (case-insensitive)
    if computed_checksum.lower() != expected_checksum.lower():
        raise ChecksumError(
            f"Checksum mismatch for {file_path}: "
            f"expected {expected_checksum}, got {computed_checksum}"
        )
