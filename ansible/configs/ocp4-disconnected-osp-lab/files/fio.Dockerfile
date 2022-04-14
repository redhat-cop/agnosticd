FROM fedora:latest
RUN dnf install -y jq fio nmap-ncat
COPY ./fio-test.sh /tmp/fio-test.sh
