#!/usr/bin/bash

(
# Go to script's directory
cd $(dirname $0)

rc=0

# Check for python test files with invalid names
test_dirs=$(find . -type d -name 'test')
for test_dir in $test_dirs; do
    test_files=$(find $test_dir -name '*.py' | grep -v "__init__")
    for test_file in $test_files; do
        base_filename=$(basename $test_file)
        [[ ! "$base_filename" =~ ^test_.* ]] && echo "ERROR: Invalid test file name - $test_file" && rc=$(($rc+1))
    done
done

if [ "$TRAVIS_PYTHON_VERSION" != "" ]; then
    # Use always "python" executable for all Python versions in Travis
    py_cmd="python"
elif [ -f /usr/bin/python3 ]; then
    py_cmd="python3"
else
    py_cmd="python"
fi
# Find and run tests
$py_cmd -m unittest discover -v
rc=$(($rc+$?))

# Run pylint
find . -iname '*.py' | xargs pylint --rcfile=pylintrc
rc=$(($rc+$?))

exit $rc
)

