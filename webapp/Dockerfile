FROM centos:centos7
MAINTAINER Gennadii Altukhov <galt@redhat.com>

# defaults; will be overwritten by docker-compose.env
ENV POSTGRESQL_HOST=database
ENV POSTGRESQL_PORT=5432
ENV POSTGRESQL_USER=vmaas_user
ENV POSTGRESQL_PASSWORD=vmaas_passwd
ENV POSTGRESQL_DATABASE=vmaas

RUN yum -y update && yum -y install epel-release && yum -y install python-ujson python-tornado python-psycopg2 postgresql && rm -rf /var/cache/yum/*

ADD ./wait-for-postgres.sh /app/wait-for-postgres.sh
ADD ./app.py /app/app.py
ADD ./database.py /app/database.py
ADD ./updates.py /app/updates.py
ADD ./cve.py /app/cve.py
ADD ./entrypoint.sh /app/entrypoint.sh

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
