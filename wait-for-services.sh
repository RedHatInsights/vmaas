#!/usr/bin/bash
# wait-for-services.sh
# modified version from https://docs.docker.com/compose/startup-order/

trap 'echo "Stopped."; exit 1' SIGINT SIGTERM

set -e

cmd="$@"

if [ ! -z "$POSTGRESQL_DATABASE" ]; then
  >&2 echo "Checking if PostgreSQL is up"
  until python3 -c "import psycopg2;c=psycopg2.connect(host=\"$POSTGRESQL_HOST\",database=\"$POSTGRESQL_DATABASE\",user=\"$POSTGRESQL_USER\",port=\"$POSTGRESQL_PORT\",password=\"$POSTGRESQL_PASSWORD\");c.close()" &> /dev/null; do
    >&2 echo "PostgreSQL is unavailable - sleeping"
    sleep 1 &
    wait $!
  done
else
  >&2 echo "Skipping PostgreSQL check"
fi

if [ ! -z "$VMAAS_WEBSOCKET_HOST" ]; then
  >&2 echo "Checking if websocket server is up"
  until curl http://$WEBSOCKET_HOST:8082/api/v1/monitoring/health &>/dev/null; do
    >&2 echo "Websocket server is unavailable - sleeping"
    sleep 1 &
    wait $!
  done
else
  >&2 echo "Skipping websocket server check"
fi

if [ ! -z "$REPOSCAN_HOST" ]; then
  >&2 echo "Checking if reposcan API is up"
  until curl http://$REPOSCAN_HOST:8081/api/v1/monitoring/health &>/dev/null; do
    >&2 echo "Reposcan API is unavailable - sleeping"
    sleep 1 &
    wait $!
  done
else
  >&2 echo "Skipping reposcan API check"
fi

>&2 echo "Everything is up - executing command"
exec $cmd
