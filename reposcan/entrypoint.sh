#!/bin/sh

DIR=$(dirname $0)

rsync --daemon --verbose
exec $DIR/wait-for-services.sh $DIR/reposcan.py
