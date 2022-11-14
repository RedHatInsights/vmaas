#!/bin/sh

cd $(dirname $0)

if [[ ! -z $1 ]]; then
    if [[ "$1" == "webapp" ]]; then
        cd vmaas/webapp
        [[ ! -z $QE_BUILD ]] && cmd="sleep infinity" || cmd="python3 -m main"
        exec python3 -m vmaas.common.wait_for_services $cmd
    elif [[ "$1" == "webapp-go" ]]; then
        cd go/src/vmaas
        exec ./main webapp
    elif [[ "$1" == "reposcan" ]]; then
        rsync --daemon --verbose --port=$(python3 -c "import app_common_python as a;print(a.LoadedConfig.privatePort or 8730)")
        cd vmaas/reposcan
        exec python3 -m vmaas.common.wait_for_services python3 -m main
    elif [[ "$1" == "websocket" ]]; then
        cd vmaas/websocket
        exec python3 -m websocket
    elif [[ "$1" == "webapp-utils" ]]; then
        cd vmaas/webapp_utils
        exec gunicorn -c gunicorn_conf.py -w ${GUNICORN_WORKERS:-4} --bind=0.0.0.0:8083 app
    elif [[ "$1" == "sleep" ]]; then
        # "developer" mode
        echo "Sleeping ..."
        exec sleep infinity
    fi
fi

echo "Please specify service name as the first argument."
