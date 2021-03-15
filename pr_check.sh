#!/bin/bash

# source unit_test.sh

# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
APP_NAME="vulnerability"  # name of app-sre "application" folder this component lives in
COMPONENT_NAME="vmaas"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
IMAGE="quay.io/cloudservices/vmaas-app"  

IQE_PLUGINS="vulnerability"
IQE_MARKER_EXPRESSION="vmaas"
IQE_FILTER_EXPRESSION=""


# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s $CICD_URL/bootstrap.sh -o bootstrap.sh
source bootstrap.sh  # checks out bonfire and changes to "cicd" dir...

echo "$(env)"
git ls-remote origin | grep "$GIT_COMMIT"
[ "$?" -ne 0 ] && echo "Rebase your pull request, please." && exit 1

source build.sh
source deploy_ephemeral_env.sh
source smoke_test.sh

