#!/bin/bash

rc=0

for dockerfile in Dockerfile-database Dockerfile-reposcan Dockerfile-webapp Dockerfile-websocket
do
    if [ ! -f "$dockerfile" ]; then
        echo "Dockerfile '$dockerfile' doesn't exist" >&2
        rc=$(($rc+1))
    fi
    sed \
        -e "s/centos:7/registry.access.redhat.com\/rhel7/" \
        -e "s/centos\/postgresql-10-centos7/registry.access.redhat.com\/rhscl\/postgresql-10-rhel7/" \
        -e "s/yum -y install centos-release-scl/yum-config-manager --enable rhel-server-rhscl-7-rpms/" \
        "$dockerfile" | diff "${dockerfile}.rhel7" -
    diff_rc=$?
    if [ $diff_rc -gt 0 ]; then
        echo "$dockerfile and $dockerfile.rhel7 are too different!"
    else
  echo "$dockerfile and $dockerfile.rhel7 are OK"
    fi
    rc=$(($rc+$diff_rc))
done
echo ""

TESTDIR=$1
if [ ! -d "$TESTDIR" ] ; then
    echo "usage: $(basename $0) <testdir>" >&2
    exit 1
fi

(
# Go to script's directory
cd "$TESTDIR"

# Check for python test files with invalid names
test_dirs=$(find . -type d -name 'test')
for test_dir in $test_dirs; do
    test_files=$(find $test_dir -name '*.py' | grep -vE "__init__|schemas|tools|webapp_test_case|yaml_cache|conftest|db_idxs")
    for test_file in $test_files; do
        base_filename=$(basename $test_file)
        [[ ! "$base_filename" =~ ^test_.* ]] && echo "ERROR: Invalid test file name - $test_file" && rc=$(($rc+1))
    done
done

# Find and run tests
pytest --cov=. -v --color=yes
rc=$(($rc+$?))

if [ "$TESTDIR" == "websocket" ] && [ "$rc" -eq 5 ]; then
    echo "Warning: No tests for $TESTDIR found, ignore for now"
    rc=$(($rc - 5))
fi

# Run pylint
find . -iname '*.py' | xargs pylint --rcfile=../pylintrc --output-format=colorized
rc=$(($rc+$?))

# Upload to Codecov.io
codecov

exit $rc
)
