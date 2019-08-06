# Dockerfile uses postgresql 10 latest image
# with applied vmaas database schema
FROM centos/postgresql-10-centos7

# all environment variables are defined in conf/*.env
# only VMAAS_VERSION is here because we want it to be hardcoded in the image
ENV VMAAS_VERSION=latest

ENV POSTGRESQL_USER 'vmaas_admin'
ENV POSTGRESQL_PASSWORD 'vmaas_admin_pwd'
ENV POSTGRESQL_DATABASE 'vmaas'
ENV POSTGRESQL_WRITER_PASSWORD 'vmaas_writer_pwd'
ENV POSTGRESQL_READER_PASSWORD 'vmaas_reader_pwd'

ADD /database/vmaas_db_postgresql.sql ${CONTAINER_SCRIPTS_PATH}/start/
ADD /database/vmaas_user_create_postgresql.sql ${CONTAINER_SCRIPTS_PATH}/start/
ADD /database/init_schema.sh ${CONTAINER_SCRIPTS_PATH}/start/

ENV MANIFEST_PATH=/opt/app-root/manifest.txt
ENV MANIFEST_PREFIX="mgmt_services:${VMAAS_VERSION}:vmaas-database\/"
ADD /scripts/generate_manifest.sh /generate_manifest.sh
RUN /generate_manifest.sh $MANIFEST_PATH $MANIFEST_PREFIX && \
    echo 'MANIFEST:' && cat $MANIFEST_PATH
