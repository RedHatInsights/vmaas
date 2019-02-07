#!/bin/sh

cmd="$@"
exec /usr/bin/scl enable rh-python36 "$cmd"
