#!/bin/sh

function psql_exec {
    PGPASSWORD="${POSTGRESQL_PASSWORD}" psql --no-password -h "${POSTGRESQL_HOST}" -p "${POSTGRESQL_PORT}" -U "${POSTGRESQL_USER}" -d "${POSTGRESQL_DATABASE}" -t -f "$1"
}

cd $(dirname $0)

# Try to initialize schema if there are no tables (typically first run in deployments without database container - RDS)
EXISTING_TABLES=$(echo "select count(*) from pg_stat_user_tables" | psql_exec - | sed 's/[[:space:]]//g')
RETVAL=$?
if [[ "$RETVAL" == "0" && "$EXISTING_TABLES" == "0" ]]; then
    echo "Empty database, initializing..."
    psql_exec ./vmaas_user_create_postgresql.sql
    psql_exec ./vmaas_db_postgresql.sql
    echo "ALTER USER vmaas_writer WITH PASSWORD '${POSTGRESQL_WRITER_PASSWORD:-vmaas_writer_pwd}'" | psql_exec -
    echo "ALTER USER vmaas_reader WITH PASSWORD '${POSTGRESQL_READER_PASSWORD:-vmaas_reader_pwd}'" | psql_exec -
else
    exec python3 ../../wait_for_services.py python3 -m database.upgrade
fi
