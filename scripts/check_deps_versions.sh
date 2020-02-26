#!/bin/bash

CYAN='\033[0;36m'
NO_COLOR='\033[0m'
echo -e "${CYAN}Dependency updates checking...${NO_COLOR}"

# Check for python deps updates (all dirs containing Pipfile).
for APP_DIR in $(find -name Pipfile -printf '%h ')
do
    echo "Analyzing deps in '$APP_DIR'"
    cd $APP_DIR
    pipenv run pip freeze > /tmp/req.txt
    pipenv run pur -r /tmp/req.txt -o /dev/null | grep "Updated" | sed -e "s/Updated/You can update:/g"
    cd -
done
echo -e "${CYAN}------------------------------${NO_COLOR}"
