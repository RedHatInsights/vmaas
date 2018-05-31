FROM fedora:28
MAINTAINER Gennadii Altukhov <galt@redhat.com>

# defaults; will be overwritten by docker-compose.env
ENV POSTGRESQL_HOST=database
ENV POSTGRESQL_PORT=5432
ENV POSTGRESQL_USER=vmaas_reader
ENV POSTGRESQL_PASSWORD=vmaas_reader_pwd
ENV POSTGRESQL_DATABASE=vmaas

ENV REPOSCAN_WEBSOCKET_URL=ws://reposcan:8081/notifications
ENV MAX_VMAAS_SERVERS=2

RUN dnf -y update \
    && dnf install -y dnf-plugins-core \
    && dnf copr enable -y @vmaas/libs \
    && dnf -y install python3-tornado python3-psycopg2 python3-apispec postgresql python3-dateutil \
                python3-jsonschema rsync \
    && rm -rf /var/cache/dnf/*

RUN install -m 1777 -d /data
ADD ./wait-for-services.sh /app/wait-for-services.sh
ADD ./entrypoint.sh /app/
ADD ./*.py /app/
ADD ./vmaas /app/

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
