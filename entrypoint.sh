#!/bin/sh

cd $(dirname $0)

if [[ ! -z $1 ]]; then
    if [[ "$1" == "webapp" ]]; then
        cd webapp
        [[ ! -z $QE_BUILD ]] && cmd="sleep infinity" || cmd="python3 -m main"
        exec ../wait-for-services.sh "$cmd"
    elif [[ "$1" == "reposcan" ]]; then
        rsync --daemon --verbose
        cd reposcan
        exec ../wait-for-services.sh python3 -m main
    elif [[ "$1" == "websocket" ]]; then
        cd websocket
        exec python3 -m websocket
    elif [[ "$1" == "webapp-utils" ]]; then
        cd webapp_utils
        exec gunicorn -c gunicorn_conf.py -w ${GUNICORN_WORKERS:-4} --bind=0.0.0.0:8083 app
    elif [[ "$1" == "sleep" ]]; then
        # "developer" mode
        echo "Sleeping ..."
        exec sleep infinity
    fi
fi

echo "Please specify service name as the first argument."
