#!/bin/bash

# Check for python deps updates.
for req_file in */requirements*.txt requirements*.txt
do
    echo "Analyzing deps in '$req_file'"
    pur -r $req_file -o /dev/null | grep "Updated" | sed -e "s/Updated/You can update:/g"
done
