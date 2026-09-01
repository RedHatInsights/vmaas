#!/bin/bash
set -e          # Exit if a command exits with a non-zero status
set -o pipefail # Return exit status of the last command in the pipe that failed

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
TARGET_DIR="${SCRIPT_DIR}/../vmaas-go"

VERSION=$(cat ${SCRIPT_DIR}/../VERSION)

cd ${TARGET_DIR}

# Cleanup on exit (success or failure)
cleanup() {
    rm -f docs/swagger.json docs/openapi.json.tmp
}
trap cleanup EXIT

# generate the docs
# swag arguments:
# --parseDependency to include definitions from vmaas-lib
# --outputTypes to generate https://github.com/swaggo/swag/tree/master#generate-only-specific-docs-file-types
if ! swag init --parseDependency -g ./webapp/webapp.go --outputTypes json --v3.1; then
    echo "Error: swag init failed" >&2
    exit 1
fi

# Verify swagger.json was created
if [ ! -f docs/swagger.json ]; then
    echo "Error: docs/swagger.json was not generated" >&2
    exit 1
fi

# handle {{.Version}}
# replace openapi v3.1.0 with v3.0.0; FIXME: remove when `gin-swagger` will support v3.1.0
if ! cat docs/swagger.json | jq | sed "s/{{.Version}}/$VERSION/" \
| sed "s/\"openapi\": \"3\.1\.0\",/\"openapi\": \"3\.0\.0\",/" > docs/openapi.json.tmp; then
    echo "Error: Failed to process swagger.json" >&2
    exit 1
fi

# Only replace the original file if processing succeeded
mv docs/openapi.json.tmp docs/openapi.json

echo "Moved swagger docs to docs/openapi.json"

cd -
