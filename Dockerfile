FROM registry.access.redhat.com/ubi9/ubi-minimal

ARG VAR_RPMS=""
RUN curl -o /etc/yum.repos.d/postgresql.repo \
        https://copr.fedorainfracloud.org/coprs/g/insights/postgresql-16/repo/epel-9/group_insights-postgresql-16-epel-9.repo

RUN microdnf install -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python312 python3.12-pip python3-rpm python3-dnf which nginx rpm-devel git-core shadow-utils diffutils systemd libicu postgresql go-toolset \
        $VAR_RPMS && \
        ln -s /usr/lib64/python3.9/site-packages/rpm /usr/lib64/python3.12/site-packages/rpm && \
        ln -s $(basename /usr/lib64/python3.9/site-packages/rpm/_rpm.*.so) /usr/lib64/python3.9/site-packages/rpm/_rpm.so && \
    microdnf clean all

WORKDIR /vmaas

ADD pyproject.toml /vmaas/
ADD poetry.lock    /vmaas/
ADD VERSION        /vmaas/

ENV LC_ALL=C.utf8
ENV LANG=C.utf8
ARG VAR_POETRY_INSTALL_OPT="--only main"
RUN pip3.12 install --upgrade pip && \
    pip3.12 install --upgrade poetry~=2.0.1 poetry-plugin-export
RUN poetry export $VAR_POETRY_INSTALL_OPT -f requirements.txt --output requirements.txt && \
    pip3.12 install -r requirements.txt

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
        curl -o /etc/pki/ca-trust/source/anchors/2022-IT-Root-CA.crt https://certs.corp.redhat.com/certs/2022-IT-Root-CA.pem && \
        update-ca-trust extract && \
        git clone https://gitlab.cee.redhat.com/vmaas/vmaas-assets.git /vmaas/repolist_git ; \
    fi

# remove testdata possibly containing vulnerable code
RUN rm -rf /vmaas/go/pkg/mod/github.com/gabriel-vasile/mimetype\@v1.4.6/testdata/

USER vmaas

ADD entrypoint.sh               /vmaas/
ADD conf                        /vmaas/conf
ADD /database                   /vmaas/database
ADD /vmaas/webapp               /vmaas/vmaas/webapp
ADD /vmaas/reposcan             /vmaas/vmaas/reposcan
ADD /vmaas/common               /vmaas/vmaas/common

ADD /vmaas/reposcan/redhatrelease/gen_package_profile.py /usr/local/bin
