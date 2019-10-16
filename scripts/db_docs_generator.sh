#!/bin/bash

GIT_DOCS="db_docs"
VMAAS_DB_SCHEMA="vmaas_db_postgresql.sql"
VMAAS_DB_MASTER="./db_docs/vmaas_database_master"
VMAAS_DB_STABLE="./db_docs/vmaas_database_stable"
ORIGINAL_CSUM="dbscript_csum"
DB_DOCS_OUTPUT="output"
TEMP_CSUM="new_csum"

if [[ "$TRAVIS_BRANCH" != "master" ]] && [[ "$TRAVIS_BRANCH" != "stable" ]] || [[ "$TRAVIS_PULL_REQUEST" != "false" ]]
then
    echo "Database schema is updated only on pushes into master/stable."
    exit 0
fi

if [[ "$VULNERABILITY_DOCS_TOKEN" == "" ]]
then 
    echo "Cannot find github token for pushing into docs repo."
    exit 1
fi

echo "Current branch of vmaas: ${TRAVIS_BRANCH}"

echo "Calculating checksum for ${VMAAS_DB_SCHEMA}"
cd scripts
git clone https://github.com/RedHatInsights/vulnerability-docs.git $GIT_DOCS 
sha1sum ../database/$VMAAS_DB_SCHEMA > $TEMP_CSUM 
DIFF_RESULT=0

if [[ "$TRAVIS_BRANCH" == "stable" ]]
then
    diff $TEMP_CSUM $VMAAS_DB_STABLE/$ORIGINAL_CSUM > /dev/null
    DIFF_RESULT=$?
else
    diff $TEMP_CSUM $VMAAS_DB_MASTER/$ORIGINAL_CSUM > /dev/null
    DIFF_RESULT=$?
fi

if [[ "$DIFF_RESULT" == "1" ]]
then
    echo "Commit has new changes in schema, regenerating docs"
    echo "Creating output directory for docs"
    mkdir $DB_DOCS_OUTPUT 
    sudo chmod -R 777 $DB_DOCS_OUTPUT

    echo "Starting schemaspy container and creating docs"
    cd ..
    docker-compose -f docker-compose-dbdocs.yml up --build schema_spy

    echo "Stopping containers"
    docker container stop vmaas-database

    echo "Moving the schema image"
    cd scripts
    sudo chmod -R 777 $DB_DOCS_OUTPUT
    if [[ "$TRAVIS_BRANCH" == "stable" ]]
    then
        COMMIT_MESSAGE="Updating VMAAS stable docs for commit $(git rev-parse --short HEAD)"
        rm -rf $VMAAS_DB_STABLE/*
        mv ./$DB_DOCS_OUTPUT/* $VMAAS_DB_STABLE
        mv -f $TEMP_CSUM $VMAAS_DB_STABLE/$ORIGINAL_CSUM
    else
        COMMIT_MESSAGE="Updating VMAAS master docs for commit $(git rev-parse --short HEAD)"
        rm -rf $VMAAS_DB_MASTER/*
        mv ./$DB_DOCS_OUTPUT/* $VMAAS_DB_MASTER
        mv -f $TEMP_CSUM $VMAAS_DB_MASTER/$ORIGINAL_CSUM 
    fi

    git config --global user.name "vmaas-bot"
    git config --global user.email "40663028+vmaas-bot@users.noreply.github.com"

    GIT_LOCATION="https://vmaas-bot:${VULNERABILITY_DOCS_TOKEN}@github.com/RedHatInsights/vulnerability-docs.git"

    cd $GIT_DOCS
    git add .
    git commit -m "$COMMIT_MESSAGE"
    git push "$GIT_LOCATION"
    
    cd ..
    rm -rf $DB_DOCS_OUTPUT
else
    echo "Schema is unchanged, done."
    rm $TEMP_CSUM
fi

rm -rf $GIT_DOCS
