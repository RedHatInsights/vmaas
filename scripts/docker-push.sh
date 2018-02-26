#!/bin/bash

# Variables from Travis CI environment

if [[ "$TRAVIS_BRANCH" == "master" && "$TRAVIS_PULL_REQUEST" == "false" ]]; then
    echo "$DOCKER_PASSWORD" | docker login --password-stdin -u "$DOCKER_USER"
    SERVICES=$(docker-compose config --services)
    CHANGED_FILES=$(git diff --name-only $TRAVIS_COMMIT_RANGE)
    CHANGED_SERVICES=""

    # Find changed services
    for service in $SERVICES; do
        for file in $CHANGED_FILES; do
            if echo "$file" | grep "^$service/"; then
                echo "Service $service changed."
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

