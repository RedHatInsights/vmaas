#!/bin/bash

# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
export APP_NAME="vulnerability"  # name of app-sre "application" folder this component lives in
export COMPONENT_NAME="vmaas"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
export IMAGE="quay.io/cloudservices/vmaas-app"  
export COMPONENTS="vmaas"
export COMPONENTS_W_RESOURCES="vmaas"
export CACHE_FROM_LATEST_IMAGE="true"

export IQE_PLUGINS="vmaas"
export IQE_MARKER_EXPRESSION=""
export IQE_FILTER_EXPRESSION=""
export IQE_REQUIREMENTS_PRIORITY=""
export IQE_TEST_IMPORTANCE=""
export IQE_CJI_TIMEOUT="30m"


# Heavily inspired by project-koku pr_check
# https://github.com/project-koku/koku/blob/main/pr_check.sh
export ARTIFACTS_DIR="$WORKSPACE/artifacts"
mkdir -p $ARTIFACTS_DIR
LABELS_DIR="$WORKSPACE/github_labels"


# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh
echo "creating PR image"

git clone --branch python_cicd https://github.com/psegedy/bonfire.git
git clone --branch podman_client https://github.com/RedHatInsights/bonfire-cicd.git
echo "pip install bonfire"
python3 -m pip install bonfire/
echo "python3 -m pip install bonfire-cicd"
python3 -m pip install bonfire-cicd/

bonfire cicd build
bonfire cicd deploy ephemeral
bonfire cicd smoke-tests
