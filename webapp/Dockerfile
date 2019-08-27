FROM centos:7

RUN yum -y update && \
    yum -y install centos-release-scl && \
    yum -y install rh-python36 which rsync && \
    rm -rf /var/cache/yum/*

ENV PATH=/opt/rh/rh-python36/root/usr/bin:$PATH

WORKDIR /webapp

ADD /webapp/Pipfile* /webapp/

ENV LC_ALL=en_US.utf8
RUN pip install --upgrade pip pipenv && \
    pipenv install --system && pipenv check

ENV VMAAS_VERSION=latest
ENV MANIFEST_PREFIX="mgmt_services:${VMAAS_VERSION}:vmaas-webapp\/"
ENV MANIFEST_PYTHON=python
ADD /scripts/generate_manifest.sh /generate_manifest.sh
RUN /generate_manifest.sh manifest.txt $MANIFEST_PREFIX $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat manifest.txt

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /webapp --no-create-home vmaas

USER vmaas

EXPOSE 8080

ADD /webapp/*.sh     /webapp/
ADD /webapp/*.py     /webapp/

CMD /webapp/entrypoint.sh
