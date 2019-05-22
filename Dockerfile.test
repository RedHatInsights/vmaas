FROM fedora:27

RUN dnf install -y python3 python3-pip postgresql-server findutils git

# for testing.posgres python package to find postgres commands
RUN ln -s /usr/bin/initdb /usr/local/bin/initdb && \
    ln -s /usr/bin/postgres /usr/local/bin/postgres

RUN mkdir /vmaas && cd /vmaas && mkdir reposcan webapp websocket

ADD reposcan/requirements.txt  /vmaas/reposcan
ADD webapp/requirements.txt    /vmaas/webapp
ADD websocket/requirements.txt /vmaas/websocket
ADD requirements_tests.txt     /vmaas

RUN pip3 install --upgrade pip && \
    pip3 install -r /vmaas/reposcan/requirements.txt && \
    pip3 install -r /vmaas/webapp/requirements.txt && \
    pip3 install -r /vmaas/websocket/requirements.txt && \
    pip3 install -r /vmaas/requirements_tests.txt

ADD . /vmaas

RUN chown -R postgres:postgres /vmaas

USER postgres
