#!/usr/bin/bash

if $PG_INITIALIZED ; then
    cat ${CONTAINER_SCRIPTS_PATH}/start/vmaas_db_postgresql.sql | psql -U ${POSTGRESQL_USER} -d ${POSTGRESQL_DATABASE}
else
    echo "Schema initialization skipped."
fi
