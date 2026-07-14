"""
Input validation utilities for repository metadata.
"""
import re

# Validation patterns
CVE_PATTERN = re.compile(r'^CVE-\d{4}-\d+$')
BUGZILLA_ID_PATTERN = re.compile(r'^\d+$')
PACKAGE_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9._+\-]+$')
RELEASE_PATTERN = re.compile(r'^[a-zA-Z0-9._+\-~]+$')
VERSION_PATTERN = re.compile(r'^[a-zA-Z0-9._+\-~^]+$')

# Architecture whitelist
VALID_ARCHITECTURES = {
    'noarch',
    'i386',
    'i486',
    'i586',
    'i686',
    'alpha',
    'alphaev6',
    'ia64',
    'sparc',
    'sparcv9',
    'sparc64',
    's390',
    'athlon',
    's390x',
    'ppc',
    'ppc64',
    'ppc64le',
    'pSeries',
    'iSeries',
    'x86_64',
    'ppc64iseries',
    'ppc64pseries',
    'ia32e',
    'amd64',
    'aarch64',
    'armv7hnl',
    'armv7hl',
    'armv7l',
    'armv6hl',
    'armv6l',
    'armv5tel',
    'src',
}


class ValidationError(Exception):
    """Raised when validation fails."""


def validate_cve_id(cve_id):
    """Validate CVE ID format"""
    cve_id = str(cve_id).strip()

    if not CVE_PATTERN.match(cve_id):
        raise ValidationError(f"Invalid CVE ID format: {cve_id}")

    return cve_id


def validate_bugzilla_id(bugzilla_id):
    """Validate Bugzilla ticket number format."""
    bugzilla_id = str(bugzilla_id).strip()

    if not BUGZILLA_ID_PATTERN.match(bugzilla_id):
        raise ValidationError(f"Invalid Bugzilla ID format: {bugzilla_id}")

    return bugzilla_id


def validate_architecture(arch):
    """Validate architecture name against whitelist"""
    arch = str(arch).strip()

    if arch not in VALID_ARCHITECTURES:
        raise ValidationError(f"Unknown architecture: {arch}")

    return arch


def validate_package_name(name):
    """Validate package name format"""
    name = str(name).strip()

    if not PACKAGE_NAME_PATTERN.match(name):
        raise ValidationError(f"Invalid package name format: {name}")

    return name


def validate_version(version):
    """Validate package version string"""
    version = str(version).strip()

    if not VERSION_PATTERN.match(version):
        raise ValidationError(f"Invalid version format: {version}")

    return version


def validate_release(release):
    """Validate package release string"""
    release = str(release).strip()

    if not RELEASE_PATTERN.match(release):
        raise ValidationError(f"Invalid release format: {release}")

    return release


# Field type to validator function mapping
FIELD_VALIDATORS = {
    'name': validate_package_name,
    'arch': validate_architecture,
    'version': validate_version,
    'release': validate_release,
    'cve_id': validate_cve_id,
    'bugzilla_id': validate_bugzilla_id,
}


def validate_field(value, field_type):
    """Unified validation function that validates a field based on its type"""
    validator = FIELD_VALIDATORS.get(field_type)
    if not validator:
        raise ValueError(f"Unknown field type: {field_type}")

    return validator(value)
