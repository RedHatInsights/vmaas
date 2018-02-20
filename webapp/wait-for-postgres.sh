#!/usr/bin/bash
# wait-for-postgres.sh
# modified version from https://docs.docker.com/compose/startup-order/

set -e

cmd="$@"

until PGPASSWORD="$POSTGRESQL_PASSWORD" psql -h "$POSTGRESQL_HOST" -U "$POSTGRESQL_USER" -d "$POSTGRESQL_DATABASE" -c '\q' -q 2>/dev/null; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

>&2 echo "PostgreSQL is up - executing command"
exec $cmd
