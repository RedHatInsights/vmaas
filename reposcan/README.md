# VMaaS Database population tool

### Build a new image:

```docker build -t vmaas_reposcan_img .```

### Create a container

```docker create -it --link vmaas_db_ctr:database --name vmaas_reposcan_ctr vmaas_reposcan_img```

### Start a container:

```docker start vmaas_reposcan_ctr```

### Run bash in container:

```docker exec -it vmaas_reposcan_ctr bash```


### reposcan.py is starting with container, for manual run use:

```cd /vmaas-reposcan && ./reposcan.py -d $POSTGRESQL_DATABASE -H $POSTGRESQL_HOST -U $POSTGRESQL_USER -P $POSTGRESQL_PASSWORD -r https://dl.fedoraproject.org/pub/fedora/linux/releases/25/Server/x86_64/os/```
