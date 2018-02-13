FROM centos:centos7
MAINTAINER Gennadii Altukhov <galt@redhat.com>

# defaults; will be overwritten by docker-compose.env
ENV POSTGRES_HOST=database
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=vmaas_user
ENV POSTGRES_PASSWORD=vmaas_passwd
ENV POSTGRES_DB=vmaas

RUN yum -y update && yum -y install epel-release && yum -y install python-ujson python2-falcon python-tornado python-psycopg2 postgresql && rm -rf /var/cache/yum/*

ADD ./wait-for-postgres.sh /app/wait-for-postgres.sh
ADD ./app.py /app/app.py
ADD ./errata.py /app/errata.py

EXPOSE 8080

CMD ["/app/wait-for-postgres.sh", "/app/app.py"]
