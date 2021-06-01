#!/usr/bin/env bash

# Script to lock Pipfile dependencies in container and copy generated lock file back

workdir="/tmp/"
dockerfile="Dockerfile-pipenv"

cmd=$(command -v podman)
if [[ "$cmd" == "" ]]; then
    cmd=$(command -v docker)
fi

echo "Using: $cmd"

cat <<EOF > $workdir$dockerfile
FROM registry.access.redhat.com/ubi8/ubi-minimal
RUN microdnf install python3 && microdnf clean all
RUN pip3 install --upgrade pip && pip3 install --upgrade pipenv
EOF

$cmd build -t pipenv-locker -f $dockerfile $workdir
$cmd run --rm -d --name pipenv-locker-container pipenv-locker sleep infinity
$cmd cp Pipfile pipenv-locker-container:/tmp/
$cmd exec pipenv-locker-container bash -c "cd tmp && pipenv lock"
$cmd cp pipenv-locker-container:/tmp/Pipfile.lock .
$cmd kill pipenv-locker-container
