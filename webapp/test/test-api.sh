#!/bin/sh

# fail the script immediatelly when a command fails
set -e

TEST_COMMAND="curl -s -H 'Content-Type: application/json' -X POST"
TEST_API_URL="http://localhost:8080/api/v1"
TEST_OUT=$(mktemp /tmp/vmaas-test-out.XXXXXX.json)
TEST_APIS="cves errata repos updates"

json_format () {
    python -c 'import sys, json
def sortlists(o):
    if type(o) == list:
        o.sort()
        for i in o:
            sortlists(i)
    elif type(o) == dict:
        for i in o.values():
            sortlists(i)

data = json.load(sys.stdin)
sortlists(data)
print(json.dumps(data, sort_keys=True, indent=4, separators=(",", ": ")));'
}

fail=0
for api in $TEST_APIS ; do
        for data_in in data/"$api".in.*.json ; do
                echo Testing $(basename "$data_in")
                data_out="${data_in/.in./.out.}"
                $TEST_COMMAND -d "@$data_in" "$TEST_API_URL/$api" | json_format >"$TEST_OUT"
                diff -u "$data_out" "$TEST_OUT" || let $((fail++))
        done
done

rm -f "$TEST_OUT"

if [ "$fail" -gt 0 ] ; then
    echo "$fail tests failed"
    exit 1
fi

echo "All test passed"
