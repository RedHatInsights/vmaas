FROM centos:8

RUN rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-centosofficial

RUN yum module -y install go-toolset postgresql && \
    yum -y install git rsync shadow-utils diffutils python3 python3-pip

ENV GOPATH=/go
ENV GO111MODULE=on

ADD webapp-next/go.mod  /go/src/app/
ADD webapp-next/go.sum  /go/src/app/

RUN install -m 1777 -d /data && \
    adduser --gid 0 -d /go --no-create-home vmaas

RUN chown -R vmaas:0 /go

USER vmaas

WORKDIR /go/src/app
RUN go mod download

ADD webapp-next/cache       /go/src/app/cache
ADD webapp-next/calc        /go/src/app/calc
ADD webapp-next/utils       /go/src/app/utils
ADD webapp-next/webserver   /go/src/app/webserver
ADD webapp-next/websocket   /go/src/app/websocket

ADD webapp-next/main.go     /go/src/app/
ADD webapp-next/*.sh     /go/src/app/

#RUN go build -v main.go

EXPOSE 1080

#CMD /go/src/app/wait-for-services.sh /go/src/app/main
CMD /go/src/app/wait-for-services.sh go run main.go