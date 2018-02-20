# Dockerfile uses default postgresql latest image
# with applied vmaas database schema 
FROM postgres

# Maintener
MAINTAINER Gennadii Altukhov <galt@redhat.com>

ENV POSTGRES_USER 'vmaas_user'
ENV POSTGRES_PASSWORD 'vmaas_passwd'
ENV POSTGRES_DB 'vmaas' 

ADD ./vmaas_db_postgresql.sql /docker-entrypoint-initdb.d/

# Expose port
EXPOSE 5432
