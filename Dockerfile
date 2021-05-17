FROM registry.access.redhat.com/ubi8/ubi-minimal

ADD /scripts/generate_rpm_list.sh /generate_rpm_list.sh
# make sure (redhat|centos|fedora)-release is always included in the manifest
RUN /generate_rpm_list.sh | grep -v -E "^(redhat|centos|fedora)-release" > /tmp/base_rpm_list.txt

ARG PG_REPO=https://download.postgresql.org/pub/repos/yum/12/redhat/rhel-8-x86_64/
ARG PG_RPM=postgresql12-12.2-2PGDG.rhel8.x86_64.rpm
ARG PG_LIBS_RPM=postgresql12-libs-12.2-2PGDG.rhel8.x86_64.rpm
ADD /vmaas/reposcan/RPM-GPG-KEY-PGDG /etc/pki/rpm-gpg/
RUN microdnf install python3 python3-rpm which rsync git shadow-utils diffutils systemd libicu $([ ! -z $QE_BUILD ] && echo 'procps-ng python3-coverage tar') && microdnf clean all && \
    curl -o /tmp/${PG_RPM} ${PG_REPO}${PG_RPM} && \
    curl -o /tmp/${PG_LIBS_RPM} ${PG_REPO}${PG_LIBS_RPM} && \
    rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-PGDG && \
    rpm -K /tmp/${PG_RPM} /tmp/${PG_LIBS_RPM} && \
    rpm -ivh /tmp/${PG_RPM} /tmp/${PG_LIBS_RPM} && \
    rm /tmp/${PG_RPM} /tmp/${PG_LIBS_RPM}

WORKDIR /vmaas

ADD /Pipfile* /vmaas/

ENV LC_ALL=C.utf8
ENV LANG=C.utf8
ARG PIPENV_CHECK=1
ARG PIPENV_PYUP_API_KEY=""
RUN pip3 install --upgrade pipenv && \
    pipenv install --ignore-pipfile --deploy --system && ln -s /usr/bin/python3 /usr/bin/python && \
    if [ "${PIPENV_CHECK}" == 1 ] ; then pipenv check --system -i 39462 ; fi

RUN /generate_rpm_list.sh > /tmp/final_rpm_list.txt
ENV MANIFEST_PREFIX="services-vmaas\/app"
ENV APP_BASE_IMAGE="OCI_ubi-minimal registry.access.redhat.com/ubi8"
ADD /scripts/get_app_version.sh   /get_app_version.sh
ADD /scripts/generate_manifest.sh /generate_manifest.sh
ADD /scripts/push_manifest.sh     /push_manifest.sh
ADD /vmaas/common/*.py            /vmaas/common/
ADD /vmaas/reposcan/rsyncd.conf   /etc/
RUN /generate_manifest.sh manifest.txt "$MANIFEST_PREFIX" "$APP_BASE_IMAGE" /tmp/base_rpm_list.txt /tmp/final_rpm_list.txt && \
    echo 'MANIFEST:' && cat manifest.txt

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /vmaas --no-create-home vmaas

USER vmaas

ADD .                           /vmaas/
ADD /database/*.sql             /vmaas/vmaas/reposcan/
ADD /database/upgrade/*.sh      /vmaas/vmaas/reposcan/
ADD /database/upgrade_scripts/* /vmaas/vmaas/reposcan/database/upgrade_scripts/

ENV PYTHONPATH=/vmaas

ENV COVERAGE_FILE='/tmp/.coverage'
