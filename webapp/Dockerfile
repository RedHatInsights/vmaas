FROM centos:centos7
MAINTAINER Gennadii Altukhov <galt@redhat.com>

RUN yum -y update && yum -y install epel-release python-ujson python2-falcon python-tornado python-psycopg2 && rm -rf /var/cache/yum/*

ADD ./app.py /app/app.py
ADD ./errata.py /app/errata.py
EXPOSE 8080
