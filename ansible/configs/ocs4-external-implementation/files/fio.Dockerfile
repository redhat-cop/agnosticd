FROM fedora:latest
RUN dnf install -y jq fio
COPY ./fio-test.sh /tmp/fio-test.sh
