#!/usr/bin/bash

warning="WARNING: This script will REMOVE resource requests/limits from ALL deployment configs in current project:"
filter="$1"

. ./openshift-common.sh "$warning" "$filter" "remove-resources"

