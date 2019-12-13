# VMaaS Database service

## VMaaS database upgrade system
To perform an database upgrade to VMaaS, you need to create a sql file with given upgrade changes and also edit the same changes inside the ``` vmaas_db_postgresql.sql``` file. The upgrade is performed from reposcan container (```vmaas-reposcan```).  
Step-by-step tutorial:
* Increment the number in ``` vmaas_db_postgresql.sql```, inside table db_version and perform all patch changes
* Create a SQL upgrade file
  * File needs to have name notation like, ```XXX-upgrade_name.sql``` where the XXX is the latest number of database version that you already incremented inside ```vmaas_db_postgresql.sql``` file, upgrade_name should sign upgrade meaning.
* There should not be any active running task in reposcan.
* Launch ```dbupgrade.sh``` script from reposcan container (```docker exec -it vmaas-reposcan bash dbupgrade.sh```) 
* Turn off the read-only mode in reposcan and turn on the vmaas-websocket. (```docker-compose start vmaas-websocket```)

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
