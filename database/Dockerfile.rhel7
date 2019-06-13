# Dockerfile uses postgresql 10 latest image
# with applied vmaas database schema
FROM registry.access.redhat.com/rhscl/postgresql-10-rhel7

ENV POSTGRESQL_USER 'vmaas_admin'
ENV POSTGRESQL_PASSWORD 'vmaas_admin_pwd'
ENV POSTGRESQL_DATABASE 'vmaas'
ENV POSTGRESQL_WRITER_PASSWORD 'vmaas_writer_pwd'
ENV POSTGRESQL_READER_PASSWORD 'vmaas_reader_pwd'

ADD /database/vmaas_db_postgresql.sql ${CONTAINER_SCRIPTS_PATH}/start/
ADD /database/vmaas_user_create_postgresql.sql ${CONTAINER_SCRIPTS_PATH}/start/
ADD /database/init_schema.sh ${CONTAINER_SCRIPTS_PATH}/start/
