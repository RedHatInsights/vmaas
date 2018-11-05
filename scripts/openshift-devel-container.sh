#!/usr/bin/bash

warning="WARNING: This script will OVERRIDE container entrypoint of following deployment configs:"
filter="$1"

. ./openshift-common.sh "$warning" "$filter" "devel-container"

