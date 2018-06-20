#!/bin/sh

DIR=$(dirname $0)

rsync --daemon --verbose
exec $DIR/wait-for-postgres.sh $DIR/reposcan.py
