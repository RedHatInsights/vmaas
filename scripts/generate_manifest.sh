#!/bin/sh

# ./scripts/generate_manifest.sh <DOCKERFILE> <MANIFEST_PATH>
# Example:
# ./scripts/generate_manifest.sh webapp/Dockerfile manifest_webapp.txt
# cat manifest_webapp.txt

DOCKERFILE=$1
MANIFEST_PATH=$2
DOCKER_CONTEXT=$3

echo "Dockerfile:    ${DOCKERFILE}"
echo "Manifest path: ${MANIFEST_PATH}"

# Write base image name.
echo "[base_image]" > ${MANIFEST_PATH}
cat ${DOCKERFILE} | grep "FROM" | sed -e "s/FROM //" >> ${MANIFEST_PATH}


# Build image and write out included packages (rpm, pip).
echo "Building image to inspect..."
docker build -t mf_image -f ${DOCKERFILE} .

## Write content of /etc/system-release-cpe
echo "[system-release-cpe]" >> ${MANIFEST_PATH}
docker run -it --rm mf_image bash -c "cat /etc/system-release-cpe" >> ${MANIFEST_PATH}

## Write RPM package.
echo "[rpm]" >> ${MANIFEST_PATH}
docker run -it --rm mf_image bash -c "rpm -qa" >> ${MANIFEST_PATH}

## Write Python version and packages.
echo "[python]" >> ${MANIFEST_PATH}
echo -n "python_version=" >> ${MANIFEST_PATH}
docker run -it --rm mf_image bash -c "python3 --version" >> ${MANIFEST_PATH}
docker run -it --rm mf_image bash -c "python3 -m pip freeze" >> ${MANIFEST_PATH}
