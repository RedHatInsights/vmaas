#!/bin/bash

rc=0

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
pytest --collect-only
if [ $? -ne 5 ]; then # error code 5 - No tests collected
    pytest -vvv --cov-report=xml --cov=. --color=yes --durations=1 -rP
    rc=$(($rc+$?))
fi

# Run pylint
if [ -f "../../pylintrc" ]; then
    find . -iname '*.py' | xargs pylint --rcfile=../../pylintrc --output-format=colorized
    rc=$(($rc+$?))
fi

# Run go test
if [ -f "go.sum" ]; then
    GIN_MODE=test go test -v -race -coverprofile=coverage.txt -covermode=atomic ./...
fi

exit $rc
)
