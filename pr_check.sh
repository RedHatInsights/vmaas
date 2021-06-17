#!/bin/bash

# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
APP_NAME="vulnerability"  # name of app-sre "application" folder this component lives in
COMPONENT_NAME="vmaas"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
IMAGE="quay.io/cloudservices/vmaas-app"  
COMPONENTS="vmaas"

IQE_PLUGINS="vmaas"
IQE_MARKER_EXPRESSION=""
IQE_FILTER_EXPRESSION=""

# Install bonfire repo/initialize
CICD_URL=https://raw.githubusercontent.com/psegedy/bonfire/patch-4/cicd
# curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh
set -exv

# log in to ephemeral cluster
oc login --token=$OC_LOGIN_TOKEN --server=$OC_LOGIN_SERVER

export APP_ROOT=$(pwd)
export WORKSPACE=${WORKSPACE:-$APP_ROOT}  # if running in jenkins, use the build's workspace
export BONFIRE_ROOT=${WORKSPACE}/bonfire
export CICD_ROOT=${BONFIRE_ROOT}/cicd
export IMAGE_TAG=$(git rev-parse --short=7 HEAD)
export GIT_COMMIT=$(git rev-parse HEAD)

# TODO: create custom jenkins agent image that has a lot of this stuff pre-installed
export LANG=en_US.utf-8
export LC_ALL=en_US.utf-8

python3 -m venv .bonfire_venv
source .bonfire_venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install --upgrade 'crc-bonfire>=1.0.0'

# clone repo to download cicd scripts
git clone -b patch-4 https://github.com/psegedy/bonfire.git $BONFIRE_ROOT


source $CICD_ROOT/build.sh
#source $APP_ROOT/unit_test.sh  #Add unit tests here
source $CICD_ROOT/deploy_ephemeral_env.sh
# source $CICD_ROOT/smoke_test.sh

# Spin up iqe pod and execute IQE tests in it

# Env vars defined by caller:
#IQE_PLUGINS="plugin1,plugin2" -- pytest plugins to run separated by ","
#IQE_MARKER_EXPRESSION="mymarker" -- pytest marker expression
#IQE_FILTER_EXPRESSION="something AND something_else" -- pytest filter, can be "" if no filter desired
#NAMESPACE="mynamespace" -- namespace to deploy iqe pod into, can be set by 'deploy_ephemeral_env.sh'

IQE_POD_NAME="iqe-tests"

# create a custom svc acct for the iqe pod to run with that has elevated permissions
SA=$(oc get -n $NAMESPACE sa iqe --ignore-not-found -o jsonpath='{.metadata.name}')
if [ -z "$SA" ]; then
    oc create -n $NAMESPACE sa iqe
fi
oc policy -n $NAMESPACE add-role-to-user edit system:serviceaccount:$NAMESPACE:iqe
oc secrets -n $NAMESPACE link iqe quay-cloudservices-pull --for=pull,mount

python $CICD_ROOT/iqe_pod/create_iqe_pod.py $NAMESPACE \
    -e IQE_PLUGINS=$IQE_PLUGINS \
    -e IQE_MARKER_EXPRESSION=$IQE_MARKER_EXPRESSION \
    -e IQE_FILTER_EXPRESSION=$IQE_FILTER_EXPRESSION \
    -e ENV_FOR_DYNACONF=smoke \
    -e NAMESPACE=$NAMESPACE

oc cp -n $NAMESPACE $CICD_ROOT/iqe_pod/iqe_runner.sh $IQE_POD_NAME:/iqe_venv/iqe_runner.sh
oc exec $IQE_POD_NAME -n $NAMESPACE -- bash /iqe_venv/iqe_runner.sh

oc cp -n $NAMESPACE $IQE_POD_NAME:artifacts/ $WORKSPACE/artifacts

echo "copied artifacts from iqe pod: "
ls -l $WORKSPACE/artifacts
