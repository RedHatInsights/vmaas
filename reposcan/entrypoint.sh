#!/bin/sh

DIR=$(dirname $0)

rsync --daemon --verbose
exec $DIR/wait-for-services.sh python3 -m main
