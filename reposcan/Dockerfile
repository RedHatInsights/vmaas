FROM fedora:27

# defaults; will be overwritten by docker-compose.env
ENV POSTGRESQL_HOST=database
ENV POSTGRESQL_PORT=5432
ENV POSTGRESQL_USER=vmaas_user
ENV POSTGRESQL_PASSWORD=vmaas_passwd
ENV POSTGRESQL_DATABASE=vmaas
ENV WEBAPP_API_URL=http://webapp
ENV WEBAPP_API_PORT_INTERNAL=8079
ENV REPOSCAN_SYNC_INTERVAL_MINUTES=720
ENV LOGGING_LEVEL=INFO
ENV THREADS=8
ENV CHUNK_SIZE=1048576
ENV BATCH_SIZE=100
ENV YEAR_SINCE=2002
ENV RETRY_COUNT=3

RUN dnf install -y dnf-plugins-core && dnf copr enable -y @vmaas/libs \
    && dnf install -y python3-apispec python3-psycopg2 python3-requests \
                      python3-tornado postgresql-libs postgresql \
                      python3-dateutil \
    && rm -rf /var/cache/dnf/*

# copy application to directory in a container
ADD . /vmaas-reposcan/

# remove some unnecesary files
RUN rm -rf /vmaas-reposcan/Dockerfile /vmaas-reposcan/README.md \
           /vmaas-reposcan/test_data /vmaas-reposcan/run_tests.sh \
           /vmaas-reposcan/repodata/test

EXPOSE 8081

CMD ["/vmaas-reposcan/entrypoint.sh"]
