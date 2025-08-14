#!/bin/bash

microdnf install --setopt=tsflags=nodocs -y python3.11 python3.11-pip python3.11-devel which gcc gcc-c++ make zlib-devel openssl-devel libzstd-devel zip && \
    microdnf upgrade -y && \
    microdnf clean all
set -ex && if [ -e `which python3.11` ]; then ln -s `which python3.11` /usr/local/bin/python3; fi
set -ex && if [ -e `which python3.11` ]; then ln -s `which python3.11` /usr/local/bin/python; fi
set -ex && if [ -e `which pip3.11` ]; then ln -s `which pip3.11` /usr/local/bin/pip3; fi
set -ex && if [ -e `which pip3.11` ]; then ln -s `which pip3.11` /usr/local/bin/pip; fi
microdnf install -y wget
