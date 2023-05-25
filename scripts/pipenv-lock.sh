#!/usr/bin/env bash

# Script to lock Pipfile dependencies in container and copy generated lock file back

workdir="/tmp/"
dockerfile="Dockerfile-pipenv"

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
RUN microdnf install python39 python39-pip && microdnf clean all
RUN pip3 install --upgrade pip && pip3 install --upgrade pipenv==2022.12.19
RUN [ "\$(uname -m)" == "aarch64" ] && \\
    rpm -Uvh "https://download.postgresql.org/pub/repos/yum/reporpms/EL-8-\$(uname -m)/pgdg-redhat-repo-latest.noarch.rpm" && \\
    microdnf install --disablerepo=* --enablerepo=pgdg12 --enablerepo=ubi-8-* \\
        libpq-devel && \\
    microdnf clean all || true
EOF

current_dir=$(pwd)
cd $workdir
$cmd build -t pipenv-locker -f $dockerfile .
cd $current_dir
$cmd run --rm -d --name pipenv-locker-container pipenv-locker sleep infinity
$cmd cp Pipfile pipenv-locker-container:/tmp/
$cmd exec pipenv-locker-container bash -c "cd tmp && pipenv lock"
$cmd cp pipenv-locker-container:/tmp/Pipfile.lock .
$cmd kill pipenv-locker-container
