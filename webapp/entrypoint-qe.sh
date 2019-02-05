#!/bin/sh

DIR=$(dirname $0)

exec $DIR/wait-for-services.sh sleep infinity
