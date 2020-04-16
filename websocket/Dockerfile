FROM registry.access.redhat.com/ubi8/ubi-minimal

ADD /scripts/generate_rpm_list.sh /generate_rpm_list.sh
# make sure (redhat|centos|fedora)-release is always included in the manifest
RUN /generate_rpm_list.sh | grep -v -E "^(redhat|centos|fedora)-release" > /tmp/base_rpm_list.txt

RUN microdnf install python3 which shadow-utils diffutils && microdnf clean all

WORKDIR /websocket

ADD /websocket/Pipfile* /websocket/

ENV LC_ALL=C.utf8
ENV LANG=C.utf8
ARG PIPENV_CHECK=1

RUN pip3 install --upgrade pipenv && \
    pipenv install --ignore-pipfile --deploy --system && ln -s /usr/bin/python3 /usr/bin/python && \
    if [ "${PIPENV_CHECK}" == 1 ] ; then pipenv check --system ; fi

RUN /generate_rpm_list.sh > /tmp/final_rpm_list.txt
ENV MANIFEST_PREFIX="mgmt_services:VERSION:vmaas-websocket\/"
ENV MANIFEST_PYTHON=python3
ADD /scripts/generate_manifest.sh /generate_manifest.sh
ADD /scripts/push_manifest.sh /push_manifest.sh
RUN /generate_manifest.sh manifest.txt $MANIFEST_PREFIX /tmp/base_rpm_list.txt /tmp/final_rpm_list.txt $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat manifest.txt

RUN adduser --gid 0 -d /app --no-create-home vmaas

USER vmaas

EXPOSE 8082

ADD /websocket/*.py     /websocket/
ADD /common/*.py        /websocket/common/
ADD /websocket/entrypoint.sh   /websocket/

CMD /websocket/entrypoint.sh
