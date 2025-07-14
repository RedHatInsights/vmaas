#!/bin/bash
PYTHON_VER="3.12"

microdnf install --setopt=tsflags=nodocs -y python${PYTHON_VER} python${PYTHON_VER}-pip python${PYTHON_VER}-devel which gcc gcc-c++ make zlib-devel openssl-devel libzstd-devel zip && \
    microdnf upgrade -y && \
    microdnf clean all

WHICH_PYTHON=`which python${PYTHON_VER}`
WHICH_PIP=`which pip${PYTHON_VER}`

set -ex && if [ -e ${WHICH_PYTHON} ]; then ln -s ${WHICH_PYTHON} /usr/local/bin/python3; fi
set -ex && if [ -e ${WHICH_PYTHON} ]; then ln -s ${WHICH_PYTHON} /usr/local/bin/python; fi
set -ex && if [ -e ${WHICH_PIP} ]; then ln -s ${WHICH_PIP} /usr/local/bin/pip3; fi
set -ex && if [ -e ${WHICH_PIP} ]; then ln -s ${WHICH_PIP} /usr/local/bin/pip; fi
microdnf install -y wget
