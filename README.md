# vmaas

[![Build Status](https://travis-ci.org/RedHatInsights/vmaas.svg?branch=master)](https://travis-ci.org/RedHatInsights/vmaas)

Vulnerability Management as a Service

## Quick Command Guide

### Local deployment (development)

#### All-in-one command magic

Build images and start containers

```docker-compose up```

Stop and remove containers (built images will persist)

```docker-compose down```

Stop and remove containers and database data volume (built images will persist)

```docker-compose down -v```

#### Build images

```docker-compose build```

#### Managing containers

All at once

```docker-compose start```

```docker-compose stop```

Single service

```docker-compose start database```

```docker-compose stop database```

### OpenShift deployment (stable)

Login to OpenShift cluster and select target project

```oc login <openshift URL>```

```oc project my-project```

Deploy latest builds from https://hub.docker.com/u/vmaas/

```ansible-playbook openshift-deployment.yml --tags up```

Delete deployment completely

```ansible-playbook openshift-deployment.yml --tags down```

## Initial Setup

This "Initial Setup" section was put together as I set up on my Fedora 27 system.  Your mileage may vary.

### Install docker and docker-compose

```sudo dnf install docker docker-compose```

For OpenShift deployment install also following tools.

```sudo dnf install origin-clients ansible kompose```

Start docker.

```sudo systemctl start docker```

Make sure it's working...

```sudo docker run hello-world```

If you get output that says "Hello from Docker!" you've successfully
installed Docker.  Continue the set up...

### Prepare Setup for Development

Start docker at boot.

```sudo systemctl enable docker```

Add docker group and your user to it.  This will allow you to run
docker as your user.

```sudo groupadd docker```

```sudo usermod -aG docker $USER```

Now, reboot the system to pick up the changes to the docker group.
Then log back in and test running docker as your user.

```docker run hello-world```

Look for "Hello from Docker!" again.

### First Run of VMaaS

Clone the VMaaS git repo.

```git clone https://github.com/RedHatInsights/vmaas.git```

Make sure postgresql isn't running locally... we need port 5432
available.  If anything is running on port 8080, stop that, too.

```sudo systemctl stop postgresql```

Build the images and start containers

```cd vmaas```

```docker-compose up```

Congratulations!
