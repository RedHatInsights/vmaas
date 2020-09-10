FROM registry.access.redhat.com/ubi8/ubi-minimal

ADD /scripts/generate_rpm_list.sh /generate_rpm_list.sh
# make sure (redhat|centos|fedora)-release is always included in the manifest
RUN /generate_rpm_list.sh | grep -v -E "^(redhat|centos|fedora)-release" > /tmp/base_rpm_list.txt

ARG PG_REPO=https://download.postgresql.org/pub/repos/yum/12/redhat/rhel-8-x86_64/
ARG PG_RPM=postgresql12-12.2-2PGDG.rhel8.x86_64.rpm
ARG PG_LIBS_RPM=postgresql12-libs-12.2-2PGDG.rhel8.x86_64.rpm
ADD /reposcan/RPM-GPG-KEY-PGDG /etc/pki/rpm-gpg/
RUN microdnf install python3 python3-rpm which rsync git shadow-utils diffutils systemd libicu $([ ! -z $QE_BUILD ] && echo 'procps-ng') && microdnf clean all && \
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
    if [ "${PIPENV_CHECK}" == 1 ] ; then pipenv check --system ; fi

RUN /generate_rpm_list.sh > /tmp/final_rpm_list.txt
ENV MANIFEST_PREFIX="mgmt_services:VERSION:vmaas-app\/"
ENV MANIFEST_PYTHON=python3
ADD /scripts/generate_manifest.sh /generate_manifest.sh
ADD /scripts/push_manifest.sh /push_manifest.sh
RUN /generate_manifest.sh manifest.txt $MANIFEST_PREFIX /tmp/base_rpm_list.txt /tmp/final_rpm_list.txt $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat manifest.txt

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /vmaas --no-create-home vmaas

USER vmaas

ADD wait-for-services.sh        /vmaas/
ADD entrypoint.sh               /vmaas/
ADD /common/*.py                /vmaas/webapp/common/
ADD /common/*.py                /vmaas/reposcan/common/
ADD /common/*.py                /vmaas/websocket/common/
ADD /common/*.py                /vmaas/webapp_utils/common/
ADD /webapp/*.spec.yaml         /vmaas/webapp/
ADD /webapp/*.py                /vmaas/webapp/
ADD /reposcan/*.spec.yaml       /vmaas/reposcan/
ADD /reposcan/*.py              /vmaas/reposcan/
ADD /reposcan/database/*.py     /vmaas/reposcan/database/
ADD /reposcan/download/*.py     /vmaas/reposcan/download/
ADD /reposcan/redhatcve/*.py    /vmaas/reposcan/redhatcve/
ADD /reposcan/repodata/*.py     /vmaas/reposcan/repodata/
ADD /reposcan/rsyncd.conf       /etc/
ADD /database/*.sql             /vmaas/reposcan/
ADD /database/upgrade/*.sh      /vmaas/reposcan/
ADD /database/upgrade_scripts/* /vmaas/reposcan/database/upgrade_scripts/
ADD /websocket/*.py             /vmaas/websocket/
ADD /webapp_utils/*.py          /vmaas/webapp_utils/
ADD /webapp_utils/*.yml         /vmaas/webapp_utils/
ADD /webapp_utils/database/*.py /vmaas/webapp_utils/database/


ENV COVERAGE_FILE='/tmp/.coverage'
