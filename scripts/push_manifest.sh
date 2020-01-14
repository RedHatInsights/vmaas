#!/bin/sh

# GIT_TOKEN=<GIT_TOKEN> ./scripts/push_manifest.sh <GIT_REPO> <GIT_BRANCH> <SOURCE_FILE_PATH> <GIT_FILE_PATH>
# Example:
# GIT_TOKEN=mygithubtoken ./scripts/push_manifest.sh RedHatInsights/manifests master /manifest.txt vulnerability-engine/vulnerability-engine-manager.txt

GIT_REPO=$1
GIT_BRANCH=$2
SOURCE_FILE_PATH=$3
GIT_FILE_PATH=$4

API_ENDPOINT="https://api.github.com/repos/$GIT_REPO/contents/$GIT_FILE_PATH"

if [[ ! -z $GIT_TOKEN ]]
then
    retry=0
    until [ $retry -ge 5 ]
    do
        curl -H "Authorization: token $GIT_TOKEN" -X GET $API_ENDPOINT?ref=$GIT_BRANCH | python3 -c "import json,sys;a=json.load(sys.stdin);print(a.get('content',''))" | base64 -d | diff $SOURCE_FILE_PATH -
        diff_rc=$?
        if [ $diff_rc -eq 0 ]
        then
            echo "Remote manifest is already up to date!"
            break
        fi
        # fetch remote file sha (if exists)
        remote_file_sha=$(curl -H "Authorization: token $GIT_TOKEN" -X GET $API_ENDPOINT?ref=$GIT_BRANCH | python3 -c "import json,sys;a=json.load(sys.stdin);print(a.get('sha',''))")
        # insert or update file
        echo "{\"message\": \"Updating $GIT_FILE_PATH\", \"branch\": \"$GIT_BRANCH\", \"sha\": \"$remote_file_sha\", \"content\": \"$(base64 -w 0 $SOURCE_FILE_PATH)\"}" > /tmp/commit_payload.json
        new_commit_sha=$(curl -H "Authorization: token $GIT_TOKEN" -X PUT -d "@/tmp/commit_payload.json" $API_ENDPOINT | python -c "import json,sys;a=json.load(sys.stdin);print(a.get('commit',{}).get('sha',''))")
        # commit sha returned => success
        if [[ ! -z $new_commit_sha ]]
        then
            break
        fi
        retry=$((retry+1))
        echo "Update failed, trying again after 1 second..."
        sleep 1
    done
else
    echo "GIT_TOKEN is not set, not pushing anything."
fi

