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
pipenv run pytest -vvv --cov-report=xml --cov=. --color=yes --durations=1

rc=$(($rc+$?))

if [ "$TESTDIR" == "websocket" ] && [ "$rc" -eq 5 ]; then
    echo "Warning: No tests for $TESTDIR found, ignore for now"
    rc=$(($rc - 5))
fi

# Run pylint
cd ..
find "$TESTDIR" -iname '*.py' | xargs pipenv run pylint --rcfile=pylintrc --output-format=colorized
rc=$(($rc+$?))

exit $rc
)
