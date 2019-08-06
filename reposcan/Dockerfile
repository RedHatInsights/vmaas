FROM centos:7

# all environment variables are defined in conf/*.env
# only VMAAS_VERSION is here because we want it to be hardcoded in the image
ENV VMAAS_VERSION=0.13

RUN yum -y update && \
    yum -y install centos-release-scl && \
    yum -y install rh-python36 postgresql postgresql-libs rsync && \
    rm -rf /var/cache/yum/* && \
    ln -s /opt/rh/rh-python36/root/bin/python /usr/bin/python3 && \
    ln -s /opt/rh/rh-python36/root/bin/pip    /usr/bin/pip3

ADD /reposcan/*.sh           /reposcan/
ADD /reposcan/*.py           /reposcan/
ADD /reposcan/*.txt          /reposcan/
ADD /reposcan/common/*.py    /reposcan/common/
ADD /reposcan/database/*.py  /reposcan/database/
ADD /reposcan/download/*.py  /reposcan/download/
ADD /reposcan/nistcve/*.py   /reposcan/nistcve/
ADD /reposcan/redhatcve/*.py /reposcan/redhatcve/
ADD /reposcan/repodata/*.py  /reposcan/repodata/
ADD /reposcan/rsyncd.conf    /etc/

RUN pip3 install --upgrade pip && \
    pip3 install -r /reposcan/requirements.txt

ENV MANIFEST_PATH=/reposcan/manifest.txt
ENV MANIFEST_PREFIX="mgmt_services:${VMAAS_VERSION}:vmaas-reposcan\/"
ENV MANIFEST_PYTHON=python3
ADD /scripts/generate_manifest.sh /generate_manifest.sh
RUN /generate_manifest.sh $MANIFEST_PATH $MANIFEST_PREFIX $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat $MANIFEST_PATH

RUN install -d -m 775 -g root /data && \
    adduser --gid 0 -d /reposcan --no-create-home vmaas

USER vmaas

EXPOSE 8081 8730

CMD /reposcan/entrypoint.sh
