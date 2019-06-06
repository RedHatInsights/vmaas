[![Build Status](https://travis-ci.org/RedHatInsights/vmaas.svg?branch=master)](https://travis-ci.org/RedHatInsights/vmaas)
[![codecov](https://codecov.io/gh/RedHatInsights/vmaas/branch/master/graph/badge.svg)](https://codecov.io/gh/RedHatInsights/vmaas)

# VMaaS
**V**ulnerability **M**etadata **a**s **a** **S**ervice

## What Is This Thing?
VMaaS is intended to be a microservice that has access to data connecting RPMs,
repositories, errata, and CVEs, and can answer the question "What security changes do I
have to apply to the following set of RPMs?"

The goal is to have a common set of data, that can be updated from multiple sources, and
accessed from an arbitrary number of web-service instances. To that end, `database`
contains the docker-definitions for getting the data store up and running, `webapp` is the
service that uses the data to answer a variety of vulnerability-related questions, and
`reposcan` is an example of a plugin whose job is to fill the datastore with vulnerability
information.

## What ISN'T This Thing?
VMaaS is **NOT** intended to be an inventory-management system. It doesn't 'remember'
system profiles or containers, or manage inventory workflow in any way. An
inventory-management system could use VMaaS as one source of 'health' information for the
entities being managed.

## Quick Command Guide

### Local deployment (development)

#### All-in-one command magic
~~~bash
docker-compose up      # Build images and start containers
docker-compose down    # Stop and remove containers (built images will persist)
docker-compose down -v # Stop and remove containers and database data volume (built images will persist)
~~~

#### Build images
~~~bash
docker-compose build
~~~

#### Managing containers
All at once
~~~bash
docker-compose start
docker-compose stop
~~~

Single service
~~~bash
docker-compose start vmaas_database
docker-compose stop vmaas_database
~~~

### OpenShift deployment (stable)
Login to OpenShift cluster and select target project
~~~bash
oc login <openshift URL>
oc project my-project
~~~

Deploy latest builds from https://hub.docker.com/u/vmaas/
~~~bash
ansible-playbook openshift-deployment.yml --tags up
~~~

Delete deployment completely
~~~bash
ansible-playbook openshift-deployment.yml --tags down
~~~

## Initial Setup

This "Initial Setup" section was put together as I set up on my Fedora 27 system.  Your mileage may vary.

### Install docker and docker-compose
~~~bash
sudo dnf install docker docker-compose # install packages
sudo systemctl start docker # Start docker.
sudo docker run hello-world # Make sure it's working...
~~~
If you get output that says "Hello from Docker!" you've successfully
installed Docker. Continue the set up...


For OpenShift deployment install also following tools.
~~~bash
sudo dnf install origin-clients ansible
~~~

### Prepare Setup for Development
- Start docker at boot.
- Add docker group and your user to it. This will allow you to run
docker as your user.
~~~bash
sudo systemctl enable docker
sudo groupadd docker
sudo usermod -aG docker $USER
~~~

Now, reboot the system to pick up the changes to the docker group.
Then log back in and test running docker as your user.
~~~bash
docker run hello-world
~~~
Look for "Hello from Docker!" again.

### First Run of VMaaS

#### Free ports
Make sure postgresql isn't running locally... we need port **5432**
available. If anything is running on port **8080**, stop that, too.
~~~bash
sudo systemctl stop postgresql
~~~

#### Clone, build, run
~~~bash
git clone https://github.com/RedHatInsights/vmaas.git # clone repo
cd vmaas
docker-compose up --build # build images and start containers
~~~
Use `--build` switch every time you want to rebuild project before running.'

Congratulations!

### Run tests
You can run all tests from scratch just after cloning repo using command:
~~~bash
docker-compose -f docker-compose.test.yml up --build --exit-code-from test
~~~

### Developing / Debugging
Build and start your container in "developer mode"
~~~bash
./scripts/devel-compose build --no-cache vmaas_webapp
./scripts/devel-compose up vmaas_webapp
~~~

switch inside of the container
~~~bash
./scripts/devel-compose exec vmaas_webapp bash
~~~

now your local git directory is mounted under `/git` in the container so any change
you make you can immediatelly test.

```[root@4cb6b50d0cb6 git]# python ./app.py```

Note that by default container does NOT run the application (so you can run your own modificationtion)
so if you want to run "original" (unmodified) application use

```[root@4cb6b50d0cb6 git]# /app/entrypoint.sh```
