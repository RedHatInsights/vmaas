#!/bin/bash

# --------------------------------------------
# Options that must be configured by app owner
# --------------------------------------------
APP_NAME="vulnerability"  # name of app-sre "application" folder this component lives in
COMPONENT_NAME="vmaas"  # name of app-sre "resourceTemplate" in deploy.yaml for this component
IMAGE="quay.io/cloudservices/vmaas-app"  
COMPONENTS="vmaas"
CACHE_FROM_LATEST_IMAGE="true"

export IQE_PLUGINS="vmaas"
export IQE_MARKER_EXPRESSION="not qa"
export IQE_FILTER_EXPRESSION=""
export IQE_REQUIREMENTS_PRIORITY=""
export IQE_TEST_IMPORTANCE=""
export IQE_CJI_TIMEOUT="30m"
export IQE_ENV_VARS="DYNACONF_USER_PROVIDER__rbac_enabled=false, DYNACONF_USER_PROVIDER__keycloak_crud=false"

# Heavily inspired by project-koku pr_check
# https://github.com/project-koku/koku/blob/main/pr_check.sh
export ARTIFACTS_DIR="$WORKSPACE/artifacts"
mkdir -p $ARTIFACTS_DIR
LABELS_DIR="$WORKSPACE/github_labels"

mkdir -p $LABELS_DIR
exit_code=0
task_arr=([1]="Build" [2]="Deploy" [3]="Smoke Tests")
error_arr=([1]="The PR is labeled to not build the test image" \
           [2]="The PR is labeled to not deploy to ephemeral" \
           [3]="The PR is labeled to not run smoke tests")

function check_for_labels() {
    if [ -f $LABELS_DIR/github_labels.txt ]; then
        egrep "$1" $LABELS_DIR/github_labels.txt &>/dev/null
    fi
}

function _process_requirements_labels() {
    # $1 env var to export
    # $@ labels to process
    env_var_name=$1; shift;
    labels=$@
    if [ -n "$labels" ]; then
        labels=$(echo "$labels" | sed -e 's/"//g')
        # contents of labels is different in different shells
        # it can be one of
        #   labels="REQ1\nREQ2"
        #   labels="REQ1 REQ2"
        lines=$(echo "$labels" | wc -l | xargs)
        words=$(echo "$labels" | wc -w | xargs)
        if [[ "$lines" == "1" ]] && [[ "$words" == "1" ]]; then
            export "$env_var_name=$labels"
            return
        fi
        processed=""
        for req in $labels; do
            processed="$processed$req,"
        done
        # delete extra comma
        processed="${processed%?}"
        export "$env_var_name=$processed"
    fi
}

function process_requirements_labels() {
    if [ -f $LABELS_DIR/github_labels.txt ]; then
        requirements=$(egrep "^\"[A-Z]+-[A-Z-]*\"$" $LABELS_DIR/github_labels.txt)
        requirements_priority=$(egrep "^\"(critical|high|medium|low)-requirements\"$" $LABELS_DIR/github_labels.txt | sed -e 's/-requirements//g')
        _process_requirements_labels IQE_REQUIREMENTS $requirements
        _process_requirements_labels IQE_REQUIREMENTS_PRIORITY $requirements_priority
    fi
}

function build_image() {
    source $CICD_ROOT/build.sh
}

function deploy_ephemeral() {
    source $CICD_ROOT/deploy_ephemeral_env.sh
}

function run_smoke_tests() {
    source $CICD_ROOT/cji_smoke_test.sh
}

function make_results_xml() {
cat << EOF > $WORKSPACE/artifacts/junit-pr_check.xml
<?xml version="1.0" encoding="UTF-8" ?>
<testsuite id="pr_check" name="PR Check" tests="1" failures="0">
    <testcase id="pr_check.${task_arr[$exit_code]}" name="${task_arr[$exit_code]}">
    </testcase>
</testsuite>
EOF
}

# Save PR labels into a file
set -ex
# GH_API_URL="${GITHUB_API_URL:-https://api.github.com/}"  # don't use app-sre github api mirror for now
curl -s -H "Accept: application/vnd.github.v3+json" -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/search/issues\?q\=sha:$ghprbActualCommit | jq '.items[].labels[].name' > $LABELS_DIR/github_labels.txt

if check_for_labels "keep-namespace"; then
    export RELEASE_NAMESPACE=false
fi

if check_for_labels "skip-build"; then
    echo "PR check skipped"
    exit_code=1
else
    # Install bonfire repo/initialize
    CICD_URL=https://raw.githubusercontent.com/RedHatInsights/bonfire/master/cicd
    curl -s $CICD_URL/bootstrap.sh > .cicd_bootstrap.sh && source .cicd_bootstrap.sh
    echo "creating PR image"
    build_image
fi

if [[ $exit_code == 0 ]]; then
    if check_for_labels "skip-deploy"; then
        echo "deployment to ephemeral skipped"
        exit_code=2
    else
        echo "deploying to ephemeral"
        deploy_ephemeral
        if check_for_labels "skip-tests"; then
            echo "PR smoke tests skipped"
            exit_code=3
        else
            echo "running PR smoke tests"
            set +e
            process_requirements_labels
            set -e
            echo "running vmaas smoke tests"
            run_smoke_tests
            # echo "running vmaas-go smoke tests"
            # export IQE_ENV=clowder_smoke_go
            # oc delete cji vmaas -n $NAMESPACE
            # run_smoke_tests
        fi
    fi
fi

cp $LABELS_DIR/github_labels.txt $ARTIFACTS_DIR/github_labels.txt

if [[ $exit_code != 0 ]]
then
    echo "PR check failed"
    make_results_xml
fi
