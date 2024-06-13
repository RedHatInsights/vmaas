#!/bin/bash

###########################
# This script sources the security-scan.sh script from
# https://github.com/RedHatInsights/platform-security-gh-workflow
# This script, in combination with Jenkins, scans a repo's Dockerfile
# to provide a Software Bill of Materials (SBOM) and scan security vulnerabilities.
###########################

set -exv

IMAGE_NAME="vmaas"
DOCKERFILE_LOCATION="."

# (Severity Options: negligible, low, medium, high, critical)
FAIL_ON_SEVERITY="high"

# Build on "podman" or "docker"
PODMAN_OR_DOCKER="podman"

curl -sSL https://raw.githubusercontent.com/RedHatInsights/platform-security-gh-workflow/master/jenkins/security-scan.sh | \
    sh -s "${IMAGE_NAME}" "${DOCKERFILE_LOCATION}" "${FAIL_ON_SEVERITY}" "${PODMAN_OR_DOCKER}"
