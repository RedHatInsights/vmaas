#!/usr/bin/env bash

USAGE="Usage:
$0 REPOLIST_PATH [TARGET_HOSTNAME] [WEBAPP_HOSTNAME] [AUTH_TOKEN]

Mandatory parameters:
  REPOLIST_PATH   - Path to the repolist.json file

Optional parameters:
  TARGET_HOSTNAME - Hostname of the target machine where reposcan is running (default: localhost)
  WEBAPP_HOSTNAME - Hostname of the target machine where webapp is running (default: localhost)
  AUTH_TOKEN      - GitHub token for authentication
"

CHECK_PACKAGE="bash-4.2.45-5.el7_0.4.x86_64"

wait_and_run() {
  count=60
  while [ "$count" -gt 0 ]; do
    resp="$("$@")"
    if [[ "$resp" != *"Another task already in progress"* && "$resp" != *'"running": true'* ]]; then
      echo "$resp"
      echo
      break
    fi
    ((count--))
    sleep 10
  done
  [ "$count" -gt 0 ] || exit 1
}

wait_for_cache() {
  count=60
  while [ "$count" -gt 0 ]; do
    if curl -s "${webapp_url}/api/v1/updates/${CHECK_PACKAGE}" | grep -q '"erratum":'; then
      echo "Cache refreshed"
      break
    fi
    ((count--))
    sleep 10
  done
  [ "$count" -gt 0 ] || exit 1
}

if [ "$#" -eq 0 ]; then
  echo "$USAGE" >&2
  exit 1
fi

if [[ -z "$2" || "$2" == "localhost" || "$2" == "127.0.0.1" ]]; then
  url="http://localhost:8081"
elif [[ "$2" != "http"* ]]; then
  url="https://${2}"
else
  url="$2"
fi

if [[ -z "$3" || "$3" == "localhost" || "$3" == "127.0.0.1" ]]; then
  webapp_url="http://localhost:8080"
elif [[ "$2" != "http"* ]]; then
  webapp_url="https://${3}"
else
  webapp_url="$3"
fi

if [ -n "$4" ]; then
  token="$4"
else
  token="sometoken"
fi
headers=(-H "Authorization: token $token" -H "Content-type: application/json")

printf "Step 1/4: Import Repos\nAPI Response: "
wait_and_run curl -sS "${headers[@]}" -d "@${1}" -X POST "${url}/api/v1/repos"

printf "Step 2/4: Repo + CVEmap + CVE sync\nAPI Response: "
wait_and_run curl -sS "${headers[@]}" -X PUT "${url}/api/v1/sync"

printf "Step 3/4 Check that no reposcan task is running\nAPI Response"
wait_and_run curl -sS "${headers[@]}" -X GET "${url}/api/v1/task/status"

echo "Step 4/4 Wait for webapp to load latest data and refresh cache"
wait_for_cache

echo "Done."
