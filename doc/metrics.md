# Metrics
Prometheus metrics are used to monitor components running.
For development purposes both Prometheus and Grafana containers are included in docker-compose setup.
When adding new metric, ensure it is exposed correctly using dev setup.

## Dev containers
After running `docker-compose up --build`, you can access Prometheus and Grafana web interfaces:
- Prometheus: <http://localhost:9090>
- Grafana: <http://localhost:3000>, login: admin:passwd

## How to add new metric
1. Include new metric into the code (Counter, Gauge, Histogram etc.).
2. Visualize metric in dev Grafana board (add new chart).
3. Export new board version to json and save to `monitoring/grafana/provisioning/dashboards/vmaas.json`.
4. When new metric is in production, use dashboard import and copy new json to production Grafana.
