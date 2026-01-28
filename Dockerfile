ARG ALT_REPO

FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1770267347@sha256:759f5f42d9d6ce2a705e290b7fc549e2d2cd39312c4fa345f93c02e4abb8da95 AS buildimg

ARG ALT_REPO

ARG VAR_RPMS=""
RUN (microdnf module enable -y postgresql:16 || curl -o /etc/yum.repos.d/postgresql.repo $ALT_REPO) && \
    microdnf install -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        go-toolset rpm-devel python3.12-pip cargo rust python3.12-devel libffi-devel postgresql-devel openssl-devel \
        $VAR_RPMS && \
    microdnf clean all

ADD /vmaas-go /vmaas/go/src/vmaas

WORKDIR /vmaas/go/src/vmaas
RUN go build -v main.go && go clean -cache -modcache -testcache

# Switch back to /vmaas because of golang tests running in this stage
WORKDIR /vmaas

ADD requirements.txt     /vmaas/
ADD requirements-dev.txt /vmaas/

ARG VAR_PIP_INSTALL_OPT=""
RUN pip3.12 install --upgrade pip && \
    pip3.12 install -r requirements.txt $VAR_PIP_INSTALL_OPT && \
    pip3.12 cache purge

# -------------
# runtime image
FROM registry.access.redhat.com/ubi9/ubi-minimal:9.7-1770267347@sha256:759f5f42d9d6ce2a705e290b7fc549e2d2cd39312c4fa345f93c02e4abb8da95 AS runtimeimg

ARG ALT_REPO

RUN (microdnf module enable -y postgresql:16 || curl -o /etc/yum.repos.d/postgresql.repo $ALT_REPO) && \
    microdnf install -y --setopt=install_weak_deps=0 --setopt=tsflags=nodocs \
        python312 python3-rpm python3-dnf which nginx git-core shadow-utils diffutils systemd libicu postgresql libpq curl-minimal libcurl-minimal && \
        ln -s /usr/lib64/python3.9/site-packages/rpm /usr/lib64/python3.12/site-packages/rpm && \
        ln -s $(basename /usr/lib64/python3.9/site-packages/rpm/_rpm.*.so) /usr/lib64/python3.9/site-packages/rpm/_rpm.so && \
    microdnf clean all

WORKDIR /vmaas

RUN install -d -m 775 -g root /data && \
    adduser --gid 0 -d /vmaas --no-create-home vmaas

ENV PYTHONPATH=/vmaas

USER vmaas

# Compiled Go binary
COPY --from=buildimg --chown=vmaas:root /vmaas/go/src/vmaas/main /vmaas/go/src/vmaas/

# Python deps
COPY --from=buildimg /usr/local/lib/python3.12/site-packages   /usr/local/lib/python3.12/site-packages
COPY --from=buildimg /usr/local/lib64/python3.12/site-packages /usr/local/lib64/python3.12/site-packages
COPY --from=buildimg /usr/local/bin/uvicorn                    /usr/local/bin/

COPY --from=buildimg --chown=vmaas:root /vmaas/requirements.txt /vmaas/

ADD entrypoint.sh               /vmaas/
ADD conf                        /vmaas/conf
ADD /database                   /vmaas/database
ADD /vmaas/reposcan             /vmaas/vmaas/reposcan
ADD /vmaas/common               /vmaas/vmaas/common

ADD /vmaas-go/docs/openapi.json     /vmaas/go/src/vmaas/docs/v3/

ADD /vmaas/reposcan/redhatrelease/gen_package_profile.py /usr/local/bin

ADD VERSION /vmaas/
