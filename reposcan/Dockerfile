FROM fedora:27

# defaults; will be overwritten by docker-compose.env
ENV POSTGRESQL_HOST=database
ENV POSTGRESQL_PORT=5432
ENV POSTGRESQL_USER=vmaas_user
ENV POSTGRESQL_PASSWORD=vmaas_passwd
ENV POSTGRESQL_DATABASE=vmaas

RUN yum install -y python3-psycopg2 python3-requests \
                   python3-tornado postgresql-libs postgresql \
    && rm -rf /var/cache/yum/*

# copy application to directory in a container
ADD . /vmaas-reposcan/

# remove some unnecesary files
RUN rm -rf /vmaas-reposcan/Dockerfile /vmaas-reposcan/README.md \
           /vmaas-reposcan/test_data /vmaas-reposcan/run_tests.sh \
           /vmaas-reposcan/repodata/test 

EXPOSE 8081

CMD ["/vmaas-reposcan/entrypoint.sh"]
