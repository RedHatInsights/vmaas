#!/bin/bash

# Check for python deps updates (all dirs containing Pipfile).
for APP_DIR in $(find -name Pipfile -printf '%h ')
do
    cd $APP_DIR
    echo "Analyzing deps in '$APP_DIR'"
    pipenv run pipenv update --dry-run --bare
    cd ..
done
