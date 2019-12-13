#!/bin/sh

cd $(dirname $0)

exec ./wait-for-services.sh python3 -m database.upgrade
