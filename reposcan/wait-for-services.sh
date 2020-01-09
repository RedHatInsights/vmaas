#!/usr/bin/bash
# wait-for-postgres.sh
# modified version from https://docs.docker.com/compose/startup-order/

set -e

cmd="$@"

until python3 -c "import psycopg2;c=psycopg2.connect(host=\"$POSTGRESQL_HOST\",database=\"$POSTGRESQL_DATABASE\",user=\"$POSTGRESQL_USER\",port=\"$POSTGRESQL_PORT\",password=\"$POSTGRESQL_PASSWORD\");c.close()" &> /dev/null; do
  >&2 echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

until curl http://$WEBSOCKET_HOST:8082/api/v1/monitoring/health &>/dev/null; do
  >&2 echo "Websocket server is unavailable - sleeping"
  sleep 1
done

>&2 echo "Everything is up - executing command"
exec $cmd
