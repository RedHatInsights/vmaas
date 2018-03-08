#!/bin/bash

set -e

RELEASE_BRANCH="master"
DOCKER_COMPOSE_FILE="docker-compose.yml"

# Variables from Travis CI environment
if [[ "$TRAVIS_BRANCH" == "$RELEASE_BRANCH" && "$TRAVIS_PULL_REQUEST" == "false" ]]; then
    echo "$DOCKER_PASSWORD" | docker login --password-stdin -u "$DOCKER_USER"
    SERVICES=$(docker-compose config --services)
    if [ "$TRAVIS_COMMIT_RANGE" != "" ]; then
        COMMIT_RANGE="$TRAVIS_COMMIT_RANGE"
    else
        # $TRAVIS_COMMIT_RANGE is empty for builds triggered by the initial commit of a new branch
        COMMIT_RANGE="HEAD..master"
    fi
    CHANGED_FILES=$(git diff --name-only $COMMIT_RANGE)
    CHANGED_SERVICES=""

    # Find changed services
    for service in $SERVICES; do
        for file in $CHANGED_FILES; do
            if [ "$file" == "$DOCKER_COMPOSE_FILE" ]; then
                echo "$file changed, need to rebuild all images."
                CHANGED_SERVICES+="$service "
            elif echo "$file" | grep "^$service/"; then
                echo "Service $service changed by file $file."
                CHANGED_SERVICES+="$service "
            fi
        done
    done

    # Build changed services and push
    CHANGED_SERVICES=$(echo $CHANGED_SERVICES | tr ' ' '\n' | sort -u)
    for service in $CHANGED_SERVICES; do
        echo "Building $service image."
        docker-compose build $service
        echo "Pushing $service image."
        docker-compose push $service
    done
    docker logout
else
    echo "Docker build and push skipped."
fi

