#!/bin/bash

# Usage:
# Copy grafana json config from web UI to ./monitoring/grafana/dashboards/grafana.json and run:
# ./scripts/grafana-json-to-yaml.sh ./monitoring/grafana/dashboards/grafana.json > ./monitoring/grafana/dashboards/grafana-dashboard-clouddot-insights-vmaas.configmap.yml

PREFIX="apiVersion: v1\n\
data:\n\
  grafana.json: |"
POSTFIX="kind: ConfigMap\n\
metadata:\n\
  name: grafana-dashboard-clouddot-insights-vmaas\n\
  labels:\n\
    grafana_dashboard: \"true\"\n\
  annotations:\n\
    grafana-folder: /grafana-dashboard-definitions/Insights"

sed "1 i $PREFIX
     $ a $POSTFIX
     s/^/    /
     " $1

exit 0
{
    echo "$PREFIX"
    cat $1
    echo "$POSTFIX"
} 
