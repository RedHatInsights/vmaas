#!/bin/sh

public_port () {
    python3.12 -c "import os;import app_common_python as a;print(a.LoadedConfig.publicPort or os.getenv('BIND_PUBLIC_PORT', '8000'))"
}

private_port () {
    python3.12 -c "import os;import app_common_python as a;print(a.LoadedConfig.privatePort or os.getenv('BIND_PRIVATE_PORT', '10000'))"
}

if [[ "$#" == "0" ]]; then
    echo "Please specify service name as the first argument."
    exit 1
fi

cd "$(dirname "$0")"

if [[ "$1" == "database-upgrade" ]]; then
    set -e
    python3.12 -m vmaas.common.wait_for_services python3.12 -m vmaas.reposcan.database.upgrade
    shift
fi

if [[ ! -z $1 ]]; then
    if [[ "$1" == "webapp-go" ]]; then
        cd go/src/vmaas
        exec ./main webapp
    elif [[ "$1" == "reposcan" ]]; then
        cd vmaas/reposcan
        port=$(private_port)
        cat nginx.conf.template | sed "s/_PORT_/$port/g" > /tmp/nginx.conf
        nginx -c /tmp/nginx.conf
        port=$(public_port)
        exec python3.12 -m vmaas.common.wait_for_services uvicorn --host 0.0.0.0 --port $port --no-access-log main:app
    elif [[ "$1" == "sleep" ]]; then
        # "developer" mode
        echo "Sleeping ..."
        exec sleep infinity
    fi
fi
