#!/bin/sh

# ./scripts/generate_manifest.sh <MANIFEST_PATH> <PREFIX> <PYTHON-CMD-OPTIONAL>
# Example:
# ./scripts/generate_manifest.sh manifest_webapp.txt my-service python
# cat manifest_webapp.txt

MANIFEST_PATH=$1
PREFIX=$2
PYTHON=$3

## Write rpm packages.
rpm -qa --qf='%{sourcerpm}\n' | grep -v '(none)' | sort -u | sed 's/\.src\.rpm$//' > ${MANIFEST_PATH}

## Write Python packages if python set.
if [[ ! -z $PYTHON ]]
then
    $PYTHON -m pip freeze | sort > /tmp/pipdeps
    sed -i -e 's/^/'$PYTHON'-/' /tmp/pipdeps  # add 'python' prefix
    sed -i -e 's/==/-/' /tmp/pipdeps       # replace '==' with '-'
    sed -i -e 's/$/.pipfile/' /tmp/pipdeps # add '.pipfile' suffix
    cat /tmp/pipdeps >> ${MANIFEST_PATH}   # append python deps to manifest
fi

## Add prefix to all lines.
sed -i -e 's/^/'${PREFIX}'/' ${MANIFEST_PATH}
