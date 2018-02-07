# VMaaS Database service

### Build a new image:

```docker build -t vmaas_db_img .```

### Create a container:

```docker create -it -p 5432:5432 --name vmaas_db_ctr vmaas_db_img```

### Start a container:

```docker start vmaas_db_ctr```

### Command to connect to database

```docker exec -it vmaas_db_ctr psql -U vmaas_user --dbname vmaas```

OR

```psql -h localhost -U vmaas_user vmaas```

### Command to open shell in container

```docker exec -it vmaas_db_ctr bash```





## PostgreSQL schema creation example for the local installed database.

### Before apply sql with schema creation need to add database and user using `psql`:

```CREATE DATABASE vmaas;```

```CREATE USER vmaasuser WITH PASSWORD 'vmaaspwd';```

```GRANT ALL PRIVILEGES ON database vmaas TO vmaasuser;```

### Download vmaas_db_schema.sql and apply it.

```cat /path/to/vmaas_db_schema.sql | psql -d vmaasuser -U vmaas```
