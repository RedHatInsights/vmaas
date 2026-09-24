#!/usr/bin/env bash
# Intended to be used as an entrypoint in devserver container
# Devserver is running git server to provide vmaas-assets.git and nginx to provide downloaded CDN data
# Requires RHSM activation key to download data from Red Hat CDN

function stop {
    if [ ! -z $nginx_pid ]; then
        kill $nginx_pid
        echo "Nginx stopped."
    fi
    if [ ! -z $git_pid ]; then
        kill $git_pid
        echo "Git daemon stopped."
    fi
    exit 0
}

function download_cdn {
    subscription-manager register --org "$ACTIVATION_KEY_ORG_ID" --activationkey "$ACTIVATION_KEY"
    python3 download_repos.py repolist.in.json /data/cdn
    subscription-manager unregister
}

function generate_git {
    mkdir vmaas-assets-work
    (
        cd vmaas-assets-work
        sed 's/https:\/\/cdn\.redhat\.com/http:\/\/vmaas_devserver:8000/g' ../repolist.in.json > repolist.json
        git init
        git add .
        git config user.email "devserver@example.com"
        git config user.name "devserver"
        git commit -m "generate data"
    )
    git clone --bare vmaas-assets-work /data/gits/vmaas-assets.git
    rm -rf vmaas-assets-work
}

mkdir -p /data/cdn /data/gits

if [ ! -z "$ACTIVATION_KEY_ORG_ID" ] && [ ! -z "$ACTIVATION_KEY" ]; then
    if [ ! -d /data/cdn/content ]; then
        echo "Downloading CDN data..."
        download_cdn
    else
        echo "CDN data found, skipping download (delete the container volume if you want to re-generate)."
    fi

    if [ ! -d /data/gits/vmaas-assets.git ]; then
        echo "Generating git data..."
        generate_git
    else
        echo "Git data found, skipping generation (delete the container volume if you want to re-generate)."
    fi
else
    echo "Activation key not set! Skipping generation."
fi

nginx -c /devserver/nginx.conf -g 'daemon off;' &
nginx_pid=$!

git daemon --export-all --base-path=/data/gits &
git_pid=$!

trap stop SIGHUP SIGINT SIGQUIT SIGTERM
wait $nginx_pid $git_pid
