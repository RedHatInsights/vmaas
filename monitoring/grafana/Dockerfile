FROM grafana/grafana:11.5.1

USER root
RUN apk add --no-cache python3 py3-yaml
USER grafana

ENV GF_AUTH_ANONYMOUS_ENABLED=true
ENV GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
ENV GF_AUTH_DISABLE_LOGIN_FORM=true

ADD /scripts/extract_dashboard_configmap.py /usr/local/bin
ADD /monitoring/grafana/datasources.yml /etc/grafana/provisioning/datasources
ADD /monitoring/grafana/dashboards.yml /etc/grafana/provisioning/dashboards

ADD /monitoring/grafana/dashboards/grafana-dashboard-clouddot-insights-vmaas.configmap.yml /etc/grafana

RUN extract_dashboard_configmap.py /etc/grafana/grafana-dashboard-clouddot-insights-vmaas.configmap.yml > /etc/grafana/provisioning/dashboards/grafana-dashboard-clouddot-insights-vmaas.json
