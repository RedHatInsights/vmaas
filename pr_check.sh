#!/bin/bash

# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
APP_NAME="vulnerability"  # name of app-sre "application" folder this component lives in
COMPONENT_NAME="vmaas"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
IMAGE="quay.io/cloudservices/vmaas-app"  
COMPONENTS="vmaas"
COMPONENTS_W_RESOURCES="vmaas"
CACHE_FROM_LATEST_IMAGE="true"

IQE_PLUGINS="vmaas"
IQE_MARKER_EXPRESSION=""
IQE_FILTER_EXPRESSION=""
IQE_CJI_TIMEOUT="30m"

# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh

source $CICD_ROOT/build.sh
#source $APP_ROOT/unit_test.sh  #Add unit tests here
source $CICD_ROOT/deploy_ephemeral_env.sh
source $CICD_ROOT/cji_smoke_test.sh
