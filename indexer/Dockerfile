FROM docker.elastic.co/elasticsearch/elasticsearch:7.5.2

RUN yum install python3 rsync locales-all which -y && yum clean all
RUN mkdir /data

ENV ES_JAVA_OPTS="-Xms1g -Xmx1g"
ENV LC_ALL=en_US.utf8
ENV LANG=en_US.utf8

ADD /indexer/Pipfile* /indexer/

WORKDIR /indexer

RUN pip3 install --upgrade pipenv && \
    pipenv install --system && pipenv check

ADD ./indexer/elasticsearch.yml /usr/share/elasticsearch/config/
ADD ./indexer/*.sh /indexer/
ADD ./common/ /indexer/common/
ADD ./common/documents/* /indexer/documents/

EXPOSE 9200
EXPOSE 9300

CMD /indexer/entrypoint.sh
