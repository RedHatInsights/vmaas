FROM centos:7

ADD /scripts/generate_rpm_list.sh /generate_rpm_list.sh
# make sure (redhat|centos|fedora)-release is always included in the manifest
RUN /generate_rpm_list.sh | grep -v -E "^(redhat|centos|fedora)-release" > /tmp/base_rpm_list.txt

RUN yum -y update && \
    yum -y install centos-release-scl && \
    yum -y install rh-python36 which rsync git && \
    rm -rf /var/cache/yum/*

ENV PATH=/opt/rh/rh-python36/root/usr/bin:$PATH

WORKDIR /webapp

ADD /webapp/Pipfile* /webapp/

ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8
RUN pip install --upgrade pip pipenv && \
    pipenv install --system && pipenv check

RUN /generate_rpm_list.sh > /tmp/final_rpm_list.txt
ENV VMAAS_VERSION=latest
ENV MANIFEST_PREFIX="mgmt_services:${VMAAS_VERSION}:vmaas-webapp\/"
ENV MANIFEST_PYTHON=python
ADD /scripts/generate_manifest.sh /generate_manifest.sh
ADD /scripts/push_manifest.sh /push_manifest.sh
RUN /generate_manifest.sh $MANIFEST_PATH $MANIFEST_PREFIX /tmp/base_rpm_list.txt /tmp/final_rpm_list.txt && \
    echo 'MANIFEST:' && cat manifest.txt

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /webapp --no-create-home vmaas

USER vmaas

EXPOSE 8080

ADD /webapp/*.sh     /webapp/
ADD /webapp/*.py     /webapp/

CMD /webapp/entrypoint.sh
