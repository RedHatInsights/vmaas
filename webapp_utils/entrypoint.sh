#!/bin/sh

if [ -z $GUNICORN_WORKERS ]; then
    GUNICORN_WORKERS = 4
fi

cd $(dirname $0)
exec gunicorn -c gunicorn_conf.py -w $GUNICORN_WORKERS --bind=0.0.0.0:8083 app
