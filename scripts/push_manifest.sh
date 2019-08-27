#!/bin/sh

# GIT_TOKEN=<GIT_TOKEN> ./scripts/push_manifest.sh <GIT_REMOTE> <GIT_BRANCH> <GIT_USER> <SOURCE_FILE_PATH> <GIT_FILE_PATH>
# Example:
# GIT_TOKEN=mygithubtoken ./scripts/push_manifest.sh https://github.com/RedHatInsights/manifests.git master vulnerability-insights-bot /manifest.txt vulnerability-engine/vulnerability-engine-manager.txt

GIT_REMOTE=$1
GIT_BRANCH=$2
GIT_USER=$3
SOURCE_FILE_PATH=$4
GIT_FILE_PATH=$5

if [[ ! -z $GIT_TOKEN ]]
then
    (
        GIT_REMOTE="${GIT_REMOTE/https:\/\//https:\/\/$GIT_USER:$GIT_TOKEN@}"
        cd /tmp
        git clone $GIT_REMOTE && cd "$(basename "$GIT_REMOTE" .git)"
        git config user.email "no-reply@localhost" && git config user.name "Vulnerability Insights Bot"
        git checkout $GIT_BRANCH
	mkdir -p $(dirname $GIT_FILE_PATH) && cp $SOURCE_FILE_PATH $GIT_FILE_PATH
        git add $GIT_FILE_PATH
        git commit -m "Updating $GIT_FILE_PATH"
        retry=0
        until [ $retry -ge 5 ]
        do
            git push origin $GIT_BRANCH && break
            retry=$((retry+1))
            echo "Push failed, trying to rebase after 1 second..."
            sleep 1
            git pull -r origin $GIT_BRANCH
        done
        rm -rf $(pwd)
    )
else
    echo "GIT_TOKEN is not set, not pushing anything."
fi

