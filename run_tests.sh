#!/usr/bin/bash

TESTDIR=$1
if [ ! -d "$TESTDIR" ] ; then
    echo "usage: $(basename $0) <testdir>" >&2
    exit 1
fi

(
# Go to script's directory
cd "$TESTDIR"

rc=0

# Check for python test files with invalid names
test_dirs=$(find . -type d -name 'test')
for test_dir in $test_dirs; do
    test_files=$(find $test_dir -name '*.py' | grep -vE "__init__|schemas|tools|webapp_test_case|yaml_cache")
    for test_file in $test_files; do
        base_filename=$(basename $test_file)
        [[ ! "$base_filename" =~ ^test_.* ]] && echo "ERROR: Invalid test file name - $test_file" && rc=$(($rc+1))
    done
done

# Find and run tests
pytest --cov=. -v
rc=$(($rc+$?))

# Run pylint
find . -iname '*.py' | xargs pylint --rcfile=../pylintrc
rc=$(($rc+$?))

# Upload to Codecov.io
codecov

exit $rc
)
