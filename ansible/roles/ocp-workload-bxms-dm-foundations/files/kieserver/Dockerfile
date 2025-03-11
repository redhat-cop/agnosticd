FROM registry.redhat.io/rhdm-7/rhdm-kieserver-rhel8:7.6.0

ADD ./standalone-openshift.xml /opt/eap/standalone/configuration/standalone-openshift.xml
USER root
RUN chown jboss:root /opt/eap/standalone/configuration/standalone-openshift.xml && chmod 664 /opt/eap/standalone/configuration/standalone-openshift.xml
RUN export jbossid=$(id -u jboss);echo $jbossid;
USER $jbossid
RUN /opt/eap/bin/add-user.sh -a -u 'jboss' -p 'bpms' -g 'user,kie-server,rest-all'
