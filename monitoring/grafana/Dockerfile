FROM grafana/grafana:12.3.3@sha256:9e1e77ade304069aee3196e9a4f210830e96e80ce9a2640891eccc324b152faf

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
