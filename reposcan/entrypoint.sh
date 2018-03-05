#!/bin/sh

exec /vmaas-reposcan/wait-for-postgres.sh /vmaas-reposcan/reposcan.py
