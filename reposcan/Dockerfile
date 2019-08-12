FROM centos:7

RUN yum -y update && \
    yum -y install centos-release-scl && \
    yum -y install rh-python36 which postgresql postgresql-libs rsync && \
    rm -rf /var/cache/yum/*

ENV PATH=/opt/rh/rh-python36/root/usr/bin:$PATH

ADD /reposcan/*.sh           /reposcan/
ADD /reposcan/*.py           /reposcan/
ADD /reposcan/Pipfile*       /reposcan/
ADD /reposcan/common/*.py    /reposcan/common/
ADD /reposcan/database/*.py  /reposcan/database/
ADD /reposcan/download/*.py  /reposcan/download/
ADD /reposcan/nistcve/*.py   /reposcan/nistcve/
ADD /reposcan/redhatcve/*.py /reposcan/redhatcve/
ADD /reposcan/repodata/*.py  /reposcan/repodata/
ADD /reposcan/rsyncd.conf    /etc/

WORKDIR /reposcan

ENV LC_ALL=en_US.utf8
RUN pip install --upgrade pip pipenv && \
    pipenv install --system && pipenv check

ENV VMAAS_VERSION=latest
ENV MANIFEST_PREFIX="mgmt_services:${VMAAS_VERSION}:vmaas-reposcan\/"
ENV MANIFEST_PYTHON=python
ADD /scripts/generate_manifest.sh /generate_manifest.sh
RUN /generate_manifest.sh manifest.txt $MANIFEST_PREFIX $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat manifest.txt

RUN install -d -m 775 -g root /data && \
    adduser --gid 0 -d /reposcan --no-create-home vmaas

USER vmaas

EXPOSE 8081 8730

CMD /reposcan/entrypoint.sh
