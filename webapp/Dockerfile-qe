FROM centos:7

# all environment variables are defined in conf/reposcan.env
# only VMAAS_VERSION is here because we want it to be hardcoded in the image
ENV VMAAS_VERSION=latest

RUN yum -y update && \
    yum -y install centos-release-scl && \
    yum -y install rh-python36 rsync procps-ng && \
    rm -rf /var/cache/yum/* && \
    ln -s /opt/rh/rh-python36/root/bin/python /usr/bin/python3 && \
    ln -s /opt/rh/rh-python36/root/bin/pip    /usr/bin/pip3

ADD /webapp/*.sh  /webapp/
ADD /webapp/*.py  /webapp/
ADD /webapp/*.txt /webapp/

RUN pip3 install --upgrade pip && \
    pip3 install -r /webapp/requirements_qe.txt
    
RUN ln -s /opt/rh/rh-python36/root/bin/coverage /usr/bin/coverage

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /webapp --no-create-home vmaas

USER vmaas

ENV COVERAGE_FILE='/tmp/.coverage'

EXPOSE 8080

CMD /webapp/entrypoint-qe.sh
