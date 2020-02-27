#!/usr/bin/bash
# wait-for-services.sh
# modified version from https://docs.docker.com/compose/startup-order/

set -e

cmd="$@"

until curl http://$WEBSOCKET_HOST:8082/api/v1/monitoring/health &>/dev/null; do
  >&2 echo "Websocket server is unavailable - sleeping"
  sleep 1
done

until curl http://$REPOSCAN_HOST:8081/api/v1/monitoring/health &>/dev/null; do
  >&2 echo "Reposcan API is unavailable - sleeping"
  sleep 1
done

>&2 echo "Everything is up - executing command"
exec $cmd
