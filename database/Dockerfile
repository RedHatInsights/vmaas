# Dockerfile uses postgresql 9.6 latest image
# with applied vmaas database schema 
FROM centos/postgresql-96-centos7

# Maintener
MAINTAINER Gennadii Altukhov <galt@redhat.com>

ENV POSTGRESQL_USER 'vmaas_user'
ENV POSTGRESQL_PASSWORD 'vmaas_passwd'
ENV POSTGRESQL_DATABASE 'vmaas' 

ADD ./vmaas_db_postgresql.sql ${CONTAINER_SCRIPTS_PATH}/start/
ADD ./init_schema.sh ${CONTAINER_SCRIPTS_PATH}/start/

