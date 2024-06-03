FROM registry.access.redhat.com/ubi8/ubi-minimal

# install postgresql from COPR if not building on RHSM system (devel build)
ARG REQUIRE_RHEL="yes"
RUN RHEL_REPOS=$(microdnf repolist --enabled | grep rhel-8) ; \
    if [ "$REQUIRE_RHEL" != "yes" ] && [ -z "$RHEL_REPOS" ] ; then \
        curl -o /etc/yum.repos.d/mmraka-postgresql-12-epel-8.repo https://copr.fedorainfracloud.org/coprs/mmraka/postgresql-12/repo/epel-8/mmraka-postgresql-12-epel-8.repo ; \
    else \
        microdnf module enable postgresql:12 ; \
    fi

ARG VAR_RPMS=""
RUN microdnf module enable nginx:1.20 && \
    microdnf install --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python311 python3.11-pip python3-rpm which nginx rpm-devel git-core shadow-utils diffutils systemd libicu postgresql go-toolset \
        $VAR_RPMS && \
        ln -s /usr/lib64/python3.6/site-packages/rpm /usr/lib64/python3.11/site-packages/rpm && \
    microdnf clean all

WORKDIR /vmaas

ADD pyproject.toml /vmaas/
ADD poetry.lock    /vmaas/

ENV LC_ALL=C.utf8
ENV LANG=C.utf8
ARG VAR_POETRY_INSTALL_OPT="--only main"
RUN pip3 install --upgrade pip && \
    pip3 install --upgrade poetry~=1.5
RUN poetry export $VAR_POETRY_INSTALL_OPT -f requirements.txt --output requirements.txt && \
    pip3 install -r requirements.txt

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

# Baked-in content for FedRAMP
ARG STATIC_ASSETS=0
RUN if [ "${STATIC_ASSETS}" == 1 ] ; then \
        curl -o /etc/pki/ca-trust/source/anchors/2015-IT-Root-CA.crt https://certs.corp.redhat.com/certs/2015-IT-Root-CA.pem && \
        update-ca-trust extract && \
        git clone https://gitlab.cee.redhat.com/vmaas/vmaas-assets.git /vmaas/repolist_git ; \
    fi

USER vmaas

ADD entrypoint.sh               /vmaas/
ADD conf                        /vmaas/conf
ADD /database                   /vmaas/database
ADD /vmaas/webapp               /vmaas/vmaas/webapp
ADD /vmaas/reposcan             /vmaas/vmaas/reposcan
ADD /vmaas/common               /vmaas/vmaas/common
