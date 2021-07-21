FROM registry.access.redhat.com/ubi8/ubi-minimal

ARG PG_REPO=https://download.postgresql.org/pub/repos/yum/12/redhat/rhel-8-x86_64/
ARG PG_RPM=postgresql12-12.2-2PGDG.rhel8.x86_64.rpm
ARG PG_LIBS_RPM=postgresql12-libs-12.2-2PGDG.rhel8.x86_64.rpm
ADD /vmaas/reposcan/RPM-GPG-KEY-PGDG /etc/pki/rpm-gpg/
RUN microdnf install python3 python3-rpm which rsync git-core shadow-utils diffutils systemd libicu && microdnf clean all && \
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
    pipenv install --ignore-pipfile --deploy --system && \
    if [ "${PIPENV_CHECK}" == 1 ] ; then pipenv check --system -i 39462 ; fi

ADD /vmaas/reposcan/rsyncd.conf   /etc/

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /vmaas --no-create-home vmaas

USER vmaas

ADD entrypoint.sh               /vmaas/
ADD wait_for_services.py        /vmaas/
ADD conf                        /vmaas/conf
ADD /vmaas/webapp_utils         /vmaas/vmaas/webapp_utils/
ADD /vmaas/websocket            /vmaas/vmaas/websocket/
ADD /database/upgrade/*.sh      /vmaas/vmaas/reposcan/
ADD /database/upgrade_scripts/* /vmaas/vmaas/reposcan/database/upgrade_scripts/
ADD /vmaas/webapp               /vmaas/vmaas/webapp
ADD /vmaas/reposcan             /vmaas/vmaas/reposcan
ADD /vmaas/common               /vmaas/vmaas/common
ADD /database/*.sql             /vmaas/vmaas/reposcan/

ENV PYTHONPATH=/vmaas
