FROM centos:centos7
MAINTAINER Gennadii Altukhov <galt@redhat.com>

# defaults; will be overwritten by docker-compose.env
ENV POSTGRESQL_HOST=database
ENV POSTGRESQL_PORT=5432
ENV POSTGRESQL_USER=vmaas_reader
ENV POSTGRESQL_PASSWORD=vmaas_reader_pwd
ENV POSTGRESQL_DATABASE=vmaas

ENV REPOSCAN_WEBSOCKET_URL=ws://reposcan:8081/notifications

RUN curl -o /etc/yum.repos.d/group_vmaas-libs-epel-7.repo https://copr.fedorainfracloud.org/coprs/g/vmaas/libs/repo/epel-7/group_vmaas-libs-epel-7.repo

RUN yum -y update \
    && yum -y install epel-release \
    && yum -y install python-tornado python-psycopg2 python2-apispec postgresql python-dateutil python2-futures python2-jsonschema \
    && rm -rf /var/cache/yum/*

ADD ./wait-for-services.sh /app/wait-for-services.sh
ADD ./entrypoint.sh /app/
ADD ./*.py /app/
ADD ./vmaas /app/

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
