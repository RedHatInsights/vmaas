#!/bin/bash

REPOS=(http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/7/7Server/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/7/7.4/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/7/7Server/x86_64/optional/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/7/7.4/x86_64/optional/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/6/6Server/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/6/6.9/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/6/6Server/x86_64/optional/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/server/6/6.9/x86_64/optional/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/7/7Workstation/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/7/7.4/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/7/7Workstation/x86_64/optional/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/7/7.4/x86_64/optional/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/6/6Workstation/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/6/6.9/x86_64/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/6/6Workstation/x86_64/optional/os/ \
http://pulp-read.dist.prod.ext.phx2.redhat.com/content/dist/rhel/workstation/6/6.9/x86_64/optional/os/)


for r in ${REPOS[*]}; do
	cd /vmaas-reposcan && ./reposcan.py -d $POSTGRES_DB -H $POSTGRES_HOST -U $POSTGRES_USER -P $POSTGRES_PASSWORD -r $r
done
