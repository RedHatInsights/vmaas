#!/bin/bash

rc=0

# Check database Dockerfile consistency
dockerfile=database/Dockerfile
sed \
    -e "s/docker.io\/centos\/postgresql-12-centos7/registry.redhat.io\/rhscl\/postgresql-12-rhel7/" \
    "$dockerfile".centos | diff "$dockerfile" -
diff_rc=$?
if [ $diff_rc -gt 0 ]; then
    echo "$dockerfile and $dockerfile.centos are too different!"
else
    echo "$dockerfile and $dockerfile.centos are OK"
fi
rc=$(($rc+$diff_rc))

# Run tests.
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
pipenv run pytest -vvv --cov-report=xml --cov=. --color=yes --durations=1

rc=$(($rc+$?))

if [ "$TESTDIR" == "websocket" ] && [ "$rc" -eq 5 ]; then
    echo "Warning: No tests for $TESTDIR found, ignore for now"
    rc=$(($rc - 5))
fi

# Run pylint
find . -iname '*.py' | xargs pipenv run pylint --rcfile=../../pylintrc --output-format=colorized
rc=$(($rc+$?))

exit $rc
)
