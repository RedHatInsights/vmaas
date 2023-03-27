[![Tests](https://github.com/RedHatInsights/vmaas/actions/workflows/tests.yml/badge.svg)](https://github.com/RedHatInsights/vmaas/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/RedHatInsights/vmaas/branch/master/graph/badge.svg)](https://codecov.io/gh/RedHatInsights/vmaas)
[![GitHub release](https://img.shields.io/github/release/RedHatInsights/vmaas.svg)](https://github.com/RedHatInsights/vmaas/releases/latest)

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

### Run tests
You can run all tests from scratch just after cloning repo using command:
~~~bash
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
~~~

### Developing / Debugging
You can build and start your container in ["developer mode"](doc/developer_mode.md).
You can tune metrics using Prometheus and Grafana dev containers, see [doc/metrics.md](doc/metrics.md).
