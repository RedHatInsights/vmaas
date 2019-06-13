FROM registry.access.redhat.com/rhel7

# all environment variables are defined in conf/*.env
# only VMAAS_VERSION is here because we want it to be hardcoded in the image
ENV VMAAS_VERSION=latest

RUN yum -y update && \
    yum-config-manager --enable rhel-server-rhscl-7-rpms && \
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

RUN install -d -m 775 -g root /data && \
    adduser --gid 0 -d /reposcan --no-create-home vmaas

USER vmaas

EXPOSE 8081 8730

CMD /reposcan/entrypoint.sh
