# vmaas
Vulnerability Management as a Service

## Quick Command Guide

### Build a service

```docker-compose build```

### Managing containers

All at once

```docker-compose start```

```docker-compose stop```

Single service

```docker-compose start database```

```docker-compose stop database```

### All-in-one command magic

Build images and start containers

```docker-compose up```

Stop and remove containers (built images will persist)

```docker-compose down```


## Initial Setup

This "Initial Setup" section was put together as I set up on my Fedora 27 system.  Your mileage may vary.

### Install docker-compose
```sudo dnf install docker-compose```

### Install and Set Up docker-ce
This step came from [Get Docker CE for Fedora](https://docs.docker.com/install/linux/docker-ce/fedora/) docs.

```sudo dnf install dnf-plugins-core```

```sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo```

```sudo dnf install docker-ce```

```sudo systemctl start docker```

Make sure it's working...

```sudo docker run hello-world```

If you get output that says "Hello from Docker!" you've successfully installed Docker.  Continue the set up...

Start docker at boot

```sudo systemctl enable docker```

Add your user to the docker group so you can run as your user

```sudo usermod -aG docker $USER```

Now, reboot the system to pick up the changes to the docker group.

### First Run of VMaaS

Clone the VMaaS git repo

```git clone https://github.com/RedHatInsights/vmaas.git```

Make sure postgresql isn't running locally... we need port 5432 available

```sudo systemctl stop postgresql```

Build the images and start containers

```cd vmaas```

```docker-compose up```

Congratulations!
