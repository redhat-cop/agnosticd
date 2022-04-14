FROM registry.access.redhat.com/ubi8/ubi-init:8.3 AS haproxy

RUN yum install -y haproxy

RUN systemctl enable haproxy
EXPOSE 8443
EXPOSE 8080
EXPOSE 8929
CMD [ "/sbin/init" ]