FROM centos:7

ADD /scripts/generate_rpm_list.sh /generate_rpm_list.sh
# make sure (redhat|centos|fedora)-release is always included in the manifest
RUN /generate_rpm_list.sh | grep -v -E "^(redhat|centos|fedora)-release" > /tmp/base_rpm_list.txt

RUN yum -y install centos-release-scl && \
    yum -y install rh-python36 which rsync && \
    rm -rf /var/cache/yum/*

ENV PATH=/opt/rh/rh-python36/root/usr/bin:$PATH

WORKDIR /webapp_utils

ADD /webapp_utils/Pipfile* /webapp_utils/

ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8
RUN pip install --upgrade pip && pip install --upgrade pipenv && \
    pipenv install --system && pipenv check

RUN /generate_rpm_list.sh > /tmp/final_rpm_list.txt
ENV VMAAS_VERSION=latest
ENV MANIFEST_PREFIX="mgmt_services:${VMAAS_VERSION}:vmaas-webapp-utils\/"
ENV MANIFEST_PYTHON=python
ADD /scripts/generate_manifest.sh /generate_manifest.sh
ADD /scripts/push_manifest.sh /push_manifest.sh
RUN /generate_manifest.sh manifest.txt $MANIFEST_PREFIX /tmp/base_rpm_list.txt /tmp/final_rpm_list.txt $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat manifest.txt

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /webapp_utils --no-create-home vmaas_utils

USER vmaas_utils

EXPOSE 8083

ADD /webapp_utils/*.sh  /webapp_utils/
ADD /webapp_utils/*.py  /webapp_utils/
ADD /webapp_utils/*.yml /webapp_utils/
ADD /webapp_utils/database/*.py /webapp_utils/database/
ADD /common/*.py /webapp_utils/common/

CMD /webapp_utils/entrypoint.sh
