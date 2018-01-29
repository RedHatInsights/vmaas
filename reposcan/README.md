# VMaaS Database population tool

### Script usage:

```./reposcan.py -U myuser -P mypass -d myschema -r https://mirrors.nic.cz/fedora/linux/updates/27/x86_64/ -r https://dl.fedoraproject.org/pub/epel/7/x86_64/```

### Build a new image:

```docker build -t vmaas-reposcan reposcan```

### Start a container:

```docker run --name vmaas-reposcan --link vmaas-pg:database -ti vmaas-reposcan  bash```

### Run reposcan in container:

```cd /vmaas-reposcan && ./reposcan.py -d $POSTGRES_DB -H $POSTGRES_HOST -U $POSTGRES_USER -P POSTGRES_PASSWORD -r https://dl.fedoraproject.org/pub/fedora/linux/releases/25/Server/x86_64/os/```
