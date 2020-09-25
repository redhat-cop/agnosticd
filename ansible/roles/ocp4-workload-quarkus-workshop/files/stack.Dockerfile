# To build this stack:
# docker build -t quay.io/username/quarkus-workshop-stack:VVV -f stack.Dockerfile .
# docker push quay.io/username/quarkus-workshop-stack:VVVV

FROM registry.redhat.io/codeready-workspaces/plugin-java11-rhel8:latest

ENV OC_VERSION=4.5
ENV GRAALVM_VERSION=19.3.1
ENV QUARKUS_VERSION=1.3.4.Final-redhat-00001
ENV GRAALVM_HOME="/usr/local/graalvm-ce-java11-${GRAALVM_VERSION}"
ENV PATH="/usr/local/maven/apache-maven-${MVN_VERSION}/bin:${PATH}"

USER root

RUN wget -O /tmp/oc.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/oc/${OC_VERSION}/linux/oc.tar.gz && cd /usr/bin && tar -xvzf /tmp/oc.tar.gz && chmod a+x /usr/bin/oc && rm -f /tmp/oc.tar.gz

RUN wget -O /tmp/kn.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/serverless/0.11.0/kn-linux-amd64-0.11.0.tar.gz && cd /usr/bin && tar -xvzf /tmp/kn.tar.gz ./kn && chmod a+x kn && rm -f /tmp/kn.tar.gz

RUN wget -O /tmp/tkn.tar.gz https://github.com/tektoncd/cli/releases/download/v0.7.1/tkn_0.7.1_Linux_x86_64.tar.gz && cd /usr/bin && tar -xvzf /tmp/tkn.tar.gz tkn&& chmod a+x tkn && rm -f /tmp/tkn.tar.gz

RUN sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && sudo microdnf install -y zlib-devel gcc siege && sudo curl -Lo /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && sudo chmod a+x /usr/bin/jq

RUN wget -O /tmp/graalvm.tar.gz https://github.com/graalvm/graalvm-ce-builds/releases/download/vm-${GRAALVM_VERSION}/graalvm-ce-java11-linux-amd64-${GRAALVM_VERSION}.tar.gz && cd /usr/local && tar -xvzf /tmp/graalvm.tar.gz && rm -rf /tmp/graalvm.tar.gz && ${GRAALVM_HOME}/bin/gu install native-image

USER jboss

RUN mkdir /home/jboss/.m2

COPY settings.xml /home/jboss/.m2

RUN cd /tmp && mkdir project && cd project && mvn io.quarkus:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -DplatformVersion=${QUARKUS_VERSION} -Dextensions="quarkus-agroal,quarkus-arc,quarkus-hibernate-orm,quarkus-hibernate-orm-panache,quarkus-jdbc-h2,quarkus-jdbc-postgresql,quarkus-kubernetes,quarkus-scheduler,quarkus-smallrye-fault-tolerance,quarkus-smallrye-health,quarkus-smallrye-opentracing" && mvn -f footest clean compile package && cd / && rm -rf /tmp/project

RUN cd /tmp && mkdir project && cd project && mvn io.quarkus:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -DplatformVersion=${QUARKUS_VERSION} -Dextensions="quarkus-smallrye-reactive-streams-operators,quarkus-smallrye-reactive-messaging,quarkus-smallrye-reactive-messaging-kafka,quarkus-swagger-ui,quarkus-vertx,quarkus-kafka-client, quarkus-smallrye-metrics,quarkus-smallrye-openapi" && mvn -f footest clean compile package -Pnative && cd / && rm -rf /tmp/project

RUN siege && sed -i 's/^connection = close/connection = keep-alive/' $HOME/.siege/siege.conf && sed -i 's/^benchmark = false/benchmark = true/' $HOME/.siege/siege.conf

RUN echo '-w "\n"' > $HOME/.curlrc

USER root

RUN chown -R jboss /home/jboss/.m2
RUN chmod -R a+w /home/jboss/.m2
RUN chmod -R a+rwx /home/jboss/.siege
USER jboss
