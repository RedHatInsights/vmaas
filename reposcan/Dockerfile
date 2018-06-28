FROM fedora:28

# all environment variables are defined in conf/*.env
# only VMAAS_VERSION is here because we want it to be hardcoded in the image
ENV VMAAS_VERSION=latest

RUN dnf install -y dnf-plugins-core && dnf copr enable -y @vmaas/libs \
    && dnf install -y python3-apispec python3-psycopg2 python3-requests \
                      python3-tornado postgresql-libs postgresql \
                      python3-dateutil rsync \
    && rm -rf /var/cache/dnf/*

# copy application to directory in a container
ADD . /vmaas-reposcan/
ADD rsyncd.conf /etc/

# remove some unnecesary files
RUN rm -rf /vmaas-reposcan/Dockerfile /vmaas-reposcan/README.md \
           /vmaas-reposcan/test_data /vmaas-reposcan/run_tests.sh \
           /vmaas-reposcan/repodata/test

RUN install -d -m 775 -g root /data
RUN adduser --gid 0 -d /vmaas-reposcan --no-create-home -c 'VMAAS user' vmaas
USER vmaas

EXPOSE 8081 8730

CMD ["/vmaas-reposcan/entrypoint.sh"]
