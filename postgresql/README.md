# Database schema creation scripts

PostgreSQL schema creation example.

1. Before apply sql with schema creation need to add database and user using `psql`:

```CREATE DATABASE vmaas;```

```CREATE USER vmaasuser WITH PASSWORD 'vmaaspwd';```

```GRANT ALL PRIVILEGES ON database vmaas TO vmaasuser;```

2. Downlaod vmaas_db_schema.sql and apply it.

```cat /path/to/vmaas_db_schema.sql | psql -d vmaasuser -U vmaas```
