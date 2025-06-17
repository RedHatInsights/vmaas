#!/bin/bash

SCRIPT_DIR="$(dirname "$(readlink -f "$0")")"
TARGET_DIR="${SCRIPT_DIR}/../vmaas-go"

VERSION=$(cat ${SCRIPT_DIR}/../VERSION)

cd ${TARGET_DIR}

# generate the docs
# swag arguments:
# --parseDependency to include definitions from vmaas-lib
# --outputTypes to generate https://github.com/swaggo/swag/tree/master#generate-only-specific-docs-file-types
swag init --parseDependency -g ./webapp/webapp.go --outputTypes json --v3.1

# handle {{.Version}}
# replace openapi v3.1.0 with v3.0.0; FIXME: remove when `gin-swagger` will support v3.1.0
cat docs/swagger.json | jq | sed "s/{{.Version}}/$VERSION/" \
| sed "s/\"openapi\": \"3\.1\.0\",/\"openapi\": \"3\.0\.0\",/" > docs/openapi.json

rm docs/swagger.json

cd -
