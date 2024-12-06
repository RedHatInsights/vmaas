#!/bin/sh

cd $(dirname $0)

if [[ ! -z $1 ]]; then
    if [[ "$1" == "webapp" ]]; then
        cd vmaas/webapp
        port=$(python3.12 -c "import app_common_python as a;print(a.LoadedConfig.publicPort or 8000)")
        [[ ! -z $QE_BUILD ]] && cmd="sleep infinity" || cmd="uvicorn --host 0.0.0.0 --port $port --no-access-log main:app"
        exec python3.12 -m vmaas.common.wait_for_services $cmd
    elif [[ "$1" == "webapp-go" ]]; then
        cd go/src/vmaas
        exec ./main webapp
    elif [[ "$1" == "reposcan" ]]; then
        cd vmaas/reposcan
        port=$(python3.12 -c "import app_common_python as a;print(a.LoadedConfig.privatePort or 8083)")
        cat nginx.conf.template | sed "s/_PORT_/$port/g" > /tmp/nginx.conf
        nginx -c /tmp/nginx.conf
        port=$(python3.12 -c "import app_common_python as a;print(a.LoadedConfig.publicPort or 8000)")
        exec python3.12 -m vmaas.common.wait_for_services uvicorn --host 0.0.0.0 --port $port --no-access-log main:app
    elif [[ "$1" == "sleep" ]]; then
        # "developer" mode
        echo "Sleeping ..."
        exec sleep infinity
    fi
fi

echo "Please specify service name as the first argument."
