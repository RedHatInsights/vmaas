FROM registry.access.redhat.com/ubi8/ubi-minimal

ADD /scripts/generate_rpm_list.sh /generate_rpm_list.sh
# make sure (redhat|centos|fedora)-release is always included in the manifest
RUN /generate_rpm_list.sh | grep -v -E "^(redhat|centos|fedora)-release" > /tmp/base_rpm_list.txt

RUN microdnf install python3 which rsync shadow-utils diffutils && microdnf clean all

WORKDIR /webapp

ADD /webapp/Pipfile* /webapp/

ENV LC_ALL=C.utf8
ENV LANG=C.utf8
RUN pip3 install --upgrade pipenv && \
    pipenv install --system && pipenv check -i 37752

RUN /generate_rpm_list.sh > /tmp/final_rpm_list.txt
ENV MANIFEST_PREFIX="mgmt_services:VERSION:vmaas-webapp\/"
ENV MANIFEST_PYTHON=python3
ADD /scripts/generate_manifest.sh /generate_manifest.sh
ADD /scripts/push_manifest.sh /push_manifest.sh
RUN /generate_manifest.sh manifest.txt $MANIFEST_PREFIX /tmp/base_rpm_list.txt /tmp/final_rpm_list.txt $MANIFEST_PYTHON && \
    echo 'MANIFEST:' && cat manifest.txt

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /webapp --no-create-home vmaas

USER vmaas

EXPOSE 8080

ADD /webapp/*.spec.yaml /webapp/
ADD /webapp/*.sh        /webapp/
ADD /webapp/*.py        /webapp/
ADD /common/*.py        /webapp/common/

CMD /webapp/entrypoint.sh
