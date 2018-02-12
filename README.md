# vmaas
Vulnerability Management as a Service

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
