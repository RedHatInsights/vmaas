FROM centos:7

RUN yum -y update && \
    yum -y install centos-release-scl && \
    yum -y install rh-python36 rsync && \
    rm -rf /var/cache/yum/* && \
    ln -s /opt/rh/rh-python36/root/bin/python /usr/bin/python3 && \
    ln -s /opt/rh/rh-python36/root/bin/pip    /usr/bin/pip3

ADD /websocket/*.py  /websocket/
ADD /websocket/*.txt /websocket/

RUN pip3 install --upgrade pip && \
    pip3 install -r /websocket/requirements.txt

ENV MANIFEST_PATH=/websocket/manifest.txt
ENV MANIFEST_PREFIX="mgmt_services:${VMAAS_VERSION}:vmaas-websocket\/"
ENV MANIFEST_PYTHON=python3
ADD /scripts/generate_manifest.sh /generate_manifest.sh
RUN /generate_manifest.sh $MANIFEST_PATH $MANIFEST_PREFIX $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat $MANIFEST_PATH

RUN adduser --gid 0 -d /app --no-create-home vmaas

USER vmaas

EXPOSE 8082

CMD /websocket/websocket.py
