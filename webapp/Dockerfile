FROM centos:centos7
MAINTAINER Gennadii Altukhov <galt@redhat.com>

# defaults; will be overwritten by docker-compose.env
ENV POSTGRESQL_HOST=database
ENV POSTGRESQL_PORT=5432
ENV POSTGRESQL_USER=vmaas_reader
ENV POSTGRESQL_PASSWORD=vmaas_reader_pwd
ENV POSTGRESQL_DATABASE=vmaas

RUN yum -y update \
    && yum -y install epel-release \
    && yum -y install yum-plugin-copr \
    && yum -y copr enable @vmaas/libs \
    && yum -y install python-tornado python-psycopg2 python2-apispec postgresql python-dateutil python2-jsonschema \
    && rm -rf /var/cache/yum/*

ADD ./wait-for-postgres.sh /app/wait-for-postgres.sh
ADD ./entrypoint.sh /app/
ADD ./*.py /app/
ADD ./vmaas /app/

EXPOSE 8079 8080

CMD ["/app/entrypoint.sh"]
