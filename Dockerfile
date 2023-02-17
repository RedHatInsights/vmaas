FROM registry.access.redhat.com/ubi8/ubi-minimal

# install postgresql from centos if not building on RHSM system
RUN FULL_RHEL=$(microdnf repolist --enabled | grep rhel-8) ; \
    if [ -z "$FULL_RHEL" ] ; then \
        rpm -Uvh http://mirror.centos.org/centos/8-stream/BaseOS/x86_64/os/Packages/centos-stream-repos-8-4.el8.noarch.rpm \
                 http://mirror.centos.org/centos/8-stream/BaseOS/x86_64/os/Packages/centos-gpg-keys-8-4.el8.noarch.rpm && \
        sed -i 's/^\(enabled.*\)/\1\npriority=200/;' /etc/yum.repos.d/CentOS*.repo ; \
    fi

ARG VAR_RPMS=""
RUN microdnf module enable postgresql:12 && \
    microdnf install --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python39 python39-pip python3-rpm which rsync rpm-devel git-core shadow-utils diffutils systemd libicu postgresql go-toolset \
        $VAR_RPMS && \
        ln -s /usr/lib64/python3.6/site-packages/rpm /usr/lib64/python3.9/site-packages/rpm && \
    microdnf clean all

WORKDIR /vmaas

ADD /Pipfile* /vmaas/

ENV LC_ALL=C.utf8
ENV LANG=C.utf8
ARG PIPENV_CHECK=1
ARG PIPENV_PYUP_API_KEY=""
ARG VAR_PIPENV_INSTALL_OPT=""
RUN pip3 install --upgrade pip pipenv==2022.12.19 && \
    pipenv install --ignore-pipfile --deploy --system $VAR_PIPENV_INSTALL_OPT && \
    if [ "${PIPENV_CHECK}" == 1 ] ; then pipenv check --system; fi

ADD /vmaas/reposcan/rsyncd.conf   /etc/

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /vmaas --no-create-home vmaas
RUN mkdir -p /vmaas/go/src/vmaas && chown -R vmaas:root /vmaas/go

ENV PYTHONPATH=/vmaas
ENV GOPATH=/vmaas/go \
    PATH=$PATH:/vmaas/go/bin

ADD /vmaas-go                   /vmaas/go/src/vmaas

WORKDIR /vmaas/go/src/vmaas
RUN go mod download
RUN go build -v main.go

WORKDIR /vmaas

USER vmaas

ADD entrypoint.sh               /vmaas/
ADD conf                        /vmaas/conf
ADD /database                   /vmaas/database
ADD /vmaas/webapp_utils         /vmaas/vmaas/webapp_utils/
ADD /vmaas/websocket            /vmaas/vmaas/websocket/
ADD /vmaas/webapp               /vmaas/vmaas/webapp
ADD /vmaas/reposcan             /vmaas/vmaas/reposcan
ADD /vmaas/common               /vmaas/vmaas/common
