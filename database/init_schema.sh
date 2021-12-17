#!/usr/bin/bash

if $PG_INITIALIZED ; then
    cat ${CONTAINER_SCRIPTS_PATH}/start/vmaas_user_create_postgresql.sql | psql -d ${POSTGRESQL_DATABASE}
    cat ${CONTAINER_SCRIPTS_PATH}/start/vmaas_db_postgresql.sql | psql -U ${POSTGRESQL_USER} -d ${POSTGRESQL_DATABASE}
    psql -c "ALTER USER vmaas_writer WITH PASSWORD '${POSTGRESQL_WRITER_PASSWORD}'" -d ${POSTGRESQL_DATABASE}
    psql -c "ALTER USER vmaas_reader WITH PASSWORD '${POSTGRESQL_READER_PASSWORD}'" -d ${POSTGRESQL_DATABASE}
    # Need to make sure admin role has createrole attribute
    psql -c "ALTER USER ${POSTGRESQL_USER} WITH CREATEROLE" -d ${POSTGRESQL_DATABASE}
    psql -c "ALTER USER ${POSTGRESQL_USER} WITH SUPERUSER"
else
    echo "Schema initialization skipped."
fi
