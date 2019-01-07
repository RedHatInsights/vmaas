FROM fedora:28
MAINTAINER Gennadii Altukhov <galt@redhat.com>

# all environment variables are defined in conf/reposcan.env
# only VMAAS_VERSION is here because we want it to be hardcoded in the image
ENV VMAAS_VERSION=latest

RUN dnf -y update \
    && dnf install -y dnf-plugins-core \
    && dnf copr enable -y @vmaas/libs \
    && dnf -y install python3-tornado python3-psycopg2 python3-apispec postgresql python3-dateutil \
                python3-jsonschema python3-pip rsync \
    && pip3 install prometheus_client \
    && rm -rf /var/cache/dnf/*

RUN install -m 1777 -d /data
ADD ./wait-for-services.sh /app/wait-for-services.sh
ADD ./entrypoint.sh /app/
ADD ./*.py /app/
ADD ./vmaas /app/

RUN adduser --gid 0 -d /app --no-create-home -c 'VMAAS user' vmaas
USER vmaas

EXPOSE 8080

CMD ["/app/entrypoint.sh"]
