# To build this stack:
# docker build -t quay.io/sshaaf/sso-workshop-stack:VVV -f stack.Dockerfile .
# docker push quay.io/sshaaf/sso-workshop-stack:VVVV

FROM registry.redhat.io/codeready-workspaces/plugin-java11-rhel8:latest

ENV OC_VERSION=4.10
ENV MVN_VERSION=3.8.4
ENV PATH="/usr/local/maven/apache-maven-${MVN_VERSION}/bin:${PATH}"

USER root

RUN wget -O /tmp/mvn.tar.gz https://archive.apache.org/dist/maven/maven-3/${MVN_VERSION}/binaries/apache-maven-${MVN_VERSION}-bin.tar.gz && sudo tar -xvzf /tmp/mvn.tar.gz && rm -rf /tmp/mvn.tar.gz && mkdir /usr/local/maven && mv apache-maven-${MVN_VERSION}/ /usr/local/maven/ && alternatives --install /usr/bin/mvn mvn /usr/local/maven/apache-maven-${MVN_VERSION}/bin/mvn 1

RUN wget -O /tmp/oc.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OC_VERSION}.4/openshift-client-linux-${OC_VERSION}.4.tar.gz && cd /usr/bin && sudo tar -xvzf /tmp/oc.tar.gz && sudo chmod a+x /usr/bin/oc && rm -f /tmp/oc.tar.gz

RUN sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && sudo microdnf install -y zlib-devel gcc siege gcc-c++ && sudo curl -Lo /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && sudo chmod a+x /usr/bin/jq

USER jboss

RUN mkdir /home/jboss/.m2

COPY settings.xml /home/jboss/.m2

RUN echo '-w "\n"' > $HOME/.curlrc

USER root
RUN chown -R jboss /home/jboss/.m2
RUN chmod -R a+w /home/jboss/.m2

USER jboss