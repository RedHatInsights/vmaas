#!/bin/bash

while true; do
	cd /vmaas-reposcan && ./reposcan.py -d $POSTGRESQL_DATABASE -H $POSTGRESQL_HOST -U $POSTGRESQL_USER -P $POSTGRESQL_PASSWORD --repofile dummy_repolist.txt
	# sleep for an hour
	sleep 3600
done
