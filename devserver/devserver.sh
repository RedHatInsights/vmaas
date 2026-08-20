#!/usr/bin/env bash
# Intended to be used as an entrypoint in devserver container
# Devserver is running nginx to provide vmaas-assets content and downloaded CDN data
# Requires RHSM activation key to download data from Red Hat CDN

function stop {
    if [ ! -z $nginx_pid ]; then
        kill $nginx_pid
        echo "Nginx stopped."
    fi
    exit 0
}

function download_cdn {
    subscription-manager register --org "$ACTIVATION_KEY_ORG_ID" --activationkey "$ACTIVATION_KEY"
    python3 download_repos.py repolist.in.json /data/cdn
    subscription-manager unregister
}

function generate_assets {
    sed 's/https:\/\/cdn\.redhat\.com/http:\/\/vmaas_devserver:8000/g' repolist.in.json > /data/assets/repolist.json
}

mkdir -p /data/cdn /data/assets

if [ ! -z "$ACTIVATION_KEY_ORG_ID" ] && [ ! -z "$ACTIVATION_KEY" ]; then
    if [ ! -d /data/cdn/content ]; then
        echo "Downloading CDN data..."
        download_cdn
    else
        echo "CDN data found, skipping download (delete the container volume if you want to re-generate)."
    fi

    if [ ! -f /data/assets/repolist.json ]; then
        echo "Generating assets data..."
        generate_assets
    else
        echo "Assets data found, skipping generation (delete the container volume if you want to re-generate)."
    fi
else
    echo "Activation key not set! Skipping generation."
fi

nginx -c /devserver/nginx.conf -g 'daemon off;' &
nginx_pid=$!

trap stop SIGHUP SIGINT SIGQUIT SIGTERM
wait $nginx_pid
