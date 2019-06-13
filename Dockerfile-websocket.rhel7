FROM registry.access.redhat.com/rhel7

RUN yum -y update && \
    yum-config-manager --enable rhel-server-rhscl-7-rpms && \
    yum -y install rh-python36 rsync && \
    rm -rf /var/cache/yum/* && \
    ln -s /opt/rh/rh-python36/root/bin/python /usr/bin/python3 && \
    ln -s /opt/rh/rh-python36/root/bin/pip    /usr/bin/pip3

ADD /websocket/*.py  /websocket/
ADD /websocket/*.txt /websocket/

RUN pip3 install --upgrade pip && \
    pip3 install -r /websocket/requirements.txt

RUN adduser --gid 0 -d /app --no-create-home vmaas

USER vmaas

EXPOSE 8082

CMD /websocket/websocket.py
