ARG ALT_REPO

FROM registry.access.redhat.com/hi/go:1.25.9-builder as go-builder

ARG ALT_REPO

USER root

ARG VAR_RPMS=""
RUN (microdnf module enable -y postgresql:16 || curl -o /etc/yum.repos.d/postgresql.repo $ALT_REPO) && \
    microdnf install -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        rpm-devel libffi-devel postgresql-devel openssl-devel && \
    microdnf clean all

ADD /vmaas-go /vmaas/go/src/vmaas

WORKDIR /vmaas/go/src/vmaas
RUN go build -v main.go && go clean -cache -modcache -testcache

FROM registry.access.redhat.com/hi/python:3.12.13-builder as python-builder
ARG ALT_REPO

USER root

ARG VAR_RPMS=""
RUN (microdnf module enable -y postgresql:16 || curl -o /etc/yum.repos.d/postgresql.repo $ALT_REPO) && \
    microdnf install -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        rpm-devel cargo rust libffi-devel postgresql-devel openssl-devel \
        $VAR_RPMS && \
    microdnf clean all
# Switch back to /vmaas because of golang tests running in this stage
WORKDIR /vmaas

RUN install -d -m 775 -g root data

ADD requirements.txt     /vmaas/
ADD requirements-dev.txt /vmaas/

ARG VAR_PIP_INSTALL_OPT=""
RUN pip3.12 install --upgrade pip && \
    pip3.12 install -r requirements.txt $VAR_PIP_INSTALL_OPT && \
    pip3.12 cache purge

# -------------
# runtime image
FROM registry.access.redhat.com/hi/python:3.12.13-builder as runtimeimg

USER root

ARG ALT_REPO

RUN (microdnf module enable -y postgresql:16 || curl -o /etc/yum.repos.d/postgresql.repo $ALT_REPO) && \
    microdnf install -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python3-rpm python3-dnf nginx libicu postgresql postgresql-private-libs && \
        ln -s /usr/lib64/python3.14/site-packages/rpm /usr/lib64/python3.12/site-packages/rpm && \
    microdnf clean all

WORKDIR /vmaas

ENV PYTHONPATH=/vmaas

# Compiled Go binary
COPY --from=go-builder --chown=root:root /vmaas/go/src/vmaas/main /vmaas/go/src/vmaas/

# Python deps
COPY --from=python-builder /usr/local/lib/python3.12/site-packages   /usr/local/lib/python3.12/site-packages
COPY --from=python-builder /usr/local/bin/uvicorn                    /usr/local/bin/

COPY --from=python-builder --chown=root:root /vmaas/requirements.txt /vmaas/

COPY --from=python-builder --chown=root:root /vmaas/data/ /data/

ADD entrypoint.sh               /vmaas/
ADD conf                        /vmaas/conf
ADD /database                   /vmaas/database
ADD /vmaas/reposcan             /vmaas/vmaas/reposcan
ADD /vmaas/common               /vmaas/vmaas/common

ADD /vmaas-go/docs/openapi.json     /vmaas/go/src/vmaas/docs/v3/

ADD /vmaas/reposcan/redhatrelease/gen_package_profile.py /usr/local/bin

ADD VERSION /vmaas/

USER 65532