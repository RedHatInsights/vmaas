#!/usr/bin/env bash

# Script to lock Poetry dependencies in container and copy generated lock file back

workdir="/tmp/"
dockerfile="Dockerfile-poetry"

for runtime in podman docker; do
    cmd=$(command -v $runtime)
    if [[ "$cmd" != "" ]] && $cmd ps &> /dev/null; then
        break
    else
        echo "Unable to use $runtime"
        cmd=""
    fi
done

if [[ "$cmd" != "" ]]; then
    echo "Using: $cmd"
else
    echo "No container runtime found!"
    exit 1
fi

cat <<EOF > $workdir$dockerfile
FROM registry.access.redhat.com/ubi8/ubi-minimal
RUN microdnf install --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python311 python3.11-pip python3.11-devel libpq-devel gcc git && \
    microdnf clean all
RUN pip3 install --upgrade pip && pip3 install --upgrade poetry~=1.5
EOF

current_dir=$(pwd)
cd $workdir
$cmd build -t poetry-locker -f $dockerfile .
cd $current_dir
$cmd run --rm -d --name poetry-locker-container poetry-locker sleep infinity

$cmd exec poetry-locker-container bash -c "mkdir -p /tmp"
$cmd cp "pyproject.toml" poetry-locker-container:"/tmp/"
$cmd exec poetry-locker-container bash -c "cd /tmp && poetry lock"
$cmd cp poetry-locker-container:"/tmp/poetry.lock" "."

$cmd kill poetry-locker-container
