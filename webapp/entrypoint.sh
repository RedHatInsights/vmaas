#!/bin/sh

DIR=$(dirname $0)

exec $DIR/wait-for-services.sh python3 -m main
