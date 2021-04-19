#!/bin/sh

# ./scripts/generate_manifest.sh <MANIFEST_PATH> <PREFIX> <BASE_IMAGE> <BASE_RPM_LIST> <FINAL_RPM_LIST>
# Example:
# ./scripts/generate_manifest.sh manifest.txt my-service OCI_ubi-minimal registry.access.redhat.com/ubi8 /tmp/base_rpm_list.txt /tmp/final_rpm_list.txt python3
# cat manifest.txt

MANIFEST_PATH=$1
PREFIX=$2
BASE_IMAGE=$3
BASE_RPM_LIST=$4
FINAL_RPM_LIST=$5

echo "${BASE_IMAGE}" > ${MANIFEST_PATH} # base image

grep -v -f ${BASE_RPM_LIST} ${FINAL_RPM_LIST} >> ${MANIFEST_PATH} # rpms different from base image

# Write Python packages if python is available.
if [[ -x "$(command -v python3)" ]]
then
    python3 -m pip freeze | sort > /tmp/pipdeps
    sed -i -e 's/==/-/' /tmp/pipdeps       # replace '==' with '-'
    sed -i -e 's/$/.pypi/' /tmp/pipdeps    # add '.pypi' suffix
    cat /tmp/pipdeps >> ${MANIFEST_PATH}   # append python deps to manifest
fi

# Add prefix to all lines.
VERSION="$(/get_app_version.sh)"
if [[ ! -z "$VERSION" ]]
then
    sed -i -e 's/^/'${PREFIX}\:${VERSION}\\/'/' ${MANIFEST_PATH}
else
    sed -i -e 's/^/'${PREFIX}\\/'/' ${MANIFEST_PATH}
fi
