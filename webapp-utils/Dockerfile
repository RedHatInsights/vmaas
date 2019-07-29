FROM centos:7

ENV VMAAS_VERSION=latest

RUN yum -y update && \
    yum -y install centos-release-scl && \
    yum -y install rh-python36 rsync && \
    rm -rf /var/cache/yum/* && \
    ln -s /opt/rh/rh-python36/root/bin/python /usr/bin/python3 && \
    ln -s /opt/rh/rh-python36/root/bin/pip /usr/bin/pip3

ADD /webapp-utils/*.sh  /webapp-utils/
ADD /webapp-utils/*.py  /webapp-utils/
ADD /webapp-utils/*.txt /webapp-utils/

RUN pip3 install --upgrade pip && \
    pip3 install -r /webapp-utils/requirements.txt

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /webapp-utils --no-create-home vmaas-utils

USER vmaas-utils

EXPOSE 8083

CMD bash /webapp-utils/entrypoint.sh