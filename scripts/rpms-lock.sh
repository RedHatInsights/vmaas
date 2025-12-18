#!/usr/bin/env bash

# Script to lock RPM dependencies in container and copy generated lock file back

workdir="/tmp/rpms-locker/"
dockerfile="Dockerfile-rpms"

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

mkdir -p $workdir
cat <<EOF > $workdir$dockerfile
FROM registry.access.redhat.com/ubi9/ubi
RUN dnf install -y python3 python3-pip python3-dnf skopeo rpm git-core
RUN python3 -m pip install https://github.com/konflux-ci/rpm-lockfile-prototype/archive/refs/heads/main.tar.gz
EOF

current_dir=$(pwd)
cd $workdir
$cmd build --platform linux/amd64 -t rpms-locker -f $dockerfile .
cd $current_dir
$cmd run --rm -d --name rpms-locker-container rpms-locker sleep infinity

$cmd exec rpms-locker-container bash -c "mkdir -p /tmp"
$cmd cp ".hermetic_builds/rpms.in.yaml" rpms-locker-container:"/tmp/"
$cmd exec -it rpms-locker-container bash -c "subscription-manager register"
$cmd exec -it rpms-locker-container bash -c "subscription-manager repos --enable rhel-9-for-x86_64-baseos-source-rpms --enable rhel-9-for-x86_64-appstream-source-rpms"
$cmd exec rpms-locker-container bash -c "cp /etc/yum.repos.d/redhat.repo /tmp/ && sed -i \"s/\$(uname -m)/\\\$basearch/g\" /tmp/redhat.repo"
$cmd exec rpms-locker-container bash -c "rpm-lockfile-prototype --outfile=/tmp/rpms.lock.yaml --image registry.access.redhat.com/ubi9/ubi-minimal:latest /tmp/rpms.in.yaml"

$cmd cp rpms-locker-container:"/tmp/rpms.lock.yaml" ".hermetic_builds/"
$cmd exec rpms-locker-container bash -c "subscription-manager unregister"

$cmd kill rpms-locker-container
