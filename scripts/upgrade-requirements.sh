#!/usr/bin/bash

declare -a REQUIREMENTS_FILES=("requirements_tests.txt" "webapp/requirements.txt" "webapp/requirements_qe.txt" "websocket/requirements.txt" "reposcan/requirements.txt")

set -e

echo "Checking avaiable module updates in requirements.txt files."

pip3 show pur > /dev/null
pur_status="$?"
cd ..

if [[ "$pur_status" == "1" ]]; then
    echo "Python module Pur for requirements update not found, no requirements updated."
    exit 1
fi

if [[ "$1" == "" ]]; then
    echo "Do you wanna update all requirements.txt module versions? [y/n]"
    while :
    do
        read -t 30 input

        if [[ "$input" == "y" ]]; then
            for file in "${REQUIREMENTS_FILES[@]}"
            do
                echo "$file"
                pur --requirement "$file"
                echo ""
            done
            break
        elif [[ "$input" == "n" ]] || [[ "$input" == "" ]]; then
            echo "No requirements updated."
            exit 0
        else
            echo "Please enter y/n."
            continue
        fi
    done
elif [[ "$1" == "-d" ]] || [[ "$1" == "--dry-run" ]]; then
    echo ""
    for file in "${REQUIREMENTS_FILES[@]}"
    do
        echo "$file"
        pur --requirement "$file"
        git checkout -- $file
        echo ""
    done        

    echo "DRY RUN, these requirements were not updated."
elif [[ "$1" = "-dev" ]] || [[ "$1" == "--developer" ]]; then
    exit 0
else
    echo "Unknown switch."
    exit 1
fi