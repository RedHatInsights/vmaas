FROM fedora:27

ENV POSTGRES_HOST=database
ENV POSTGRES_PORT=5432
ENV POSTGRES_USER=vmaas_user
ENV POSTGRES_PASSWORD=vmaas_passwd
ENV POSTGRES_DB=vmaas

RUN yum install -y python3-psycopg2 python3-requests \
                   postgresql-libs postgresql \
    && rm -rf /var/cache/yum/*

# copy application to directory in a container
ADD . /vmaas-reposcan/

# remove some unnecesary files
RUN rm -rf /vmaas-reposcan/Dockerfile /vmaas-reposcan/README.md \
           /vmaas-reposcan/test_data /vmaas-reposcan/run_tests.sh \
           /vmaas-reposcan/repodata/test 


CMD ["bash", "/vmaas-reposcan/dummy_crawler.sh"]
