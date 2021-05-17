# VMaaS API service

### Build a new image:

```docker build -t vmaas_webapp_img .```

### Create a container, expose port 8080, link an API container to a database one:

```docker create -it -p 8080:8080 --link vmaas_db_ctr:database --name vmaas_webapp_ctr vmaas_webapp_img```

### Start a container:

```docker start vmaas_webapp_ctr```

### Command to open shell in container

```docker exec -it vmaas_webapp_ctr bash```
