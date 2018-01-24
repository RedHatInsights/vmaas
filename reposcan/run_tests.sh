#!/usr/bin/bash

(
# Go to script's directory
cd $(dirname $0)

# Check for python test files with invalid names
test_dirs=$(find . -type d -name 'test')
for test_dir in $test_dirs; do
    test_files=$(find $test_dir -name '*.py' | grep -v "__init__")
    for test_file in $test_files; do
        base_filename=$(basename $test_file)
        [[ ! "$base_filename" =~ ^test_.* ]] && echo "ERROR: Invalid test file name - $test_file" 
    done
done

# Find and run tests
python3 -m unittest discover -v
)
