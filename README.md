[![Tests](https://github.com/RedHatInsights/vmaas/actions/workflows/tests.yml/badge.svg)](https://github.com/RedHatInsights/vmaas/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/RedHatInsights/vmaas/branch/master/graph/badge.svg)](https://codecov.io/gh/RedHatInsights/vmaas)
[![GitHub release](https://img.shields.io/github/release/RedHatInsights/vmaas.svg)](https://github.com/RedHatInsights/vmaas/releases/latest)

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

## Architecture
![](doc/schema.png)

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

### Building parameters
~~~bash
PIPENV_CHECK=0 docker-compose build # Builds images without performing "pipenv check" command
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
sudo podman-compose -f docker-compose.test.yml up --build --abort-on-container-exit
~~~

### Developing / Debugging
You can build and start your container in ["developer mode"](doc/developer_mode.md).
You can tune metrics using Prometheus and Grafana dev containers, see [doc/metrics.md](doc/metrics.md).
