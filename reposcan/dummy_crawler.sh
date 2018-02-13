#!/bin/bash

while true; do
	cd /vmaas-reposcan && ./reposcan.py -d $POSTGRES_DB -H $POSTGRES_HOST -U $POSTGRES_USER -P $POSTGRES_PASSWORD --repofile dummy_repolist.txt
	# sleep for an hour
	sleep 3600
done
