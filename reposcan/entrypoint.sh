#!/bin/sh

rsync --daemon --verbose
exec /vmaas-reposcan/wait-for-postgres.sh /vmaas-reposcan/reposcan.py
