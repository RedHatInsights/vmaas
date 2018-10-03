FROM fedora:28

RUN dnf -y update \
    && dnf -y install python3-tornado \
    && rm -rf /var/cache/dnf/*

ADD ./websocket.py /vmaas-websocket/

RUN adduser --gid 0 -d /app --no-create-home -c 'VMAAS user' vmaas
USER vmaas

EXPOSE 8082

CMD ["/vmaas-websocket/websocket.py"]
