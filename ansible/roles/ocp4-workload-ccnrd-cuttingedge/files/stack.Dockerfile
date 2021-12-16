# To build this stack:
# docker build -t quay.io/username/cloudnative-workspaces-quarkus:VVV -f stack.Dockerfile .
# docker push quay.io/username/cloudnative-workspaces-quarkus:VVVV

FROM registry.redhat.io/codeready-workspaces/plugin-java11-rhel8:latest

ENV MANDREL_VERSION=21.2.0.2-Final
ENV QUARKUS_VERSION=2.2.3.Final-redhat-00013
ENV TKN_VERSION=0.19.1
ENV KN_VERSION=0.24.0
ENV OC_VERSION=4.8
ENV MVN_VERSION=3.8.4
ENV GRAALVM_HOME="/usr/local/mandrel-java11-${MANDREL_VERSION}"
ENV PATH="/usr/local/maven/apache-maven-${MVN_VERSION}/bin:${PATH}"

USER root

RUN wget -O /tmp/mvn.tar.gz http://apache.cs.utah.edu/maven/maven-3/${MVN_VERSION}/binaries/apache-maven-${MVN_VERSION}-bin.tar.gz && sudo tar -xvzf /tmp/mvn.tar.gz && rm -rf /tmp/mvn.tar.gz && mkdir /usr/local/maven && mv apache-maven-${MVN_VERSION}/ /usr/local/maven/ && alternatives --install /usr/bin/mvn mvn /usr/local/maven/apache-maven-${MVN_VERSION}/bin/mvn 1

RUN wget -O /tmp/oc.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OC_VERSION}.3/openshift-client-linux-${OC_VERSION}.3.tar.gz && cd /usr/bin && sudo tar -xvzf /tmp/oc.tar.gz && sudo chmod a+x /usr/bin/oc && rm -f /tmp/oc.tar.gz

RUN wget -O /tmp/kn.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/serverless/${KN_VERSION}/kn-linux-amd64.tar.gz && cd /usr/bin && sudo tar -xvzf /tmp/kn.tar.gz && sudo chmod a+x kn && rm -f /tmp/kn.tar.gz

RUN wget -O /tmp/tkn.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/pipeline/${TKN_VERSION}/tkn-linux-amd64-${TKN_VERSION}.tar.gz && cd /usr/bin && sudo tar -xvzf /tmp/tkn.tar.gz && sudo chmod a+x tkn && rm -f /tmp/tkn.tar.gz

RUN sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && sudo microdnf install -y npm zlib-devel glibc-devel libffi-devel gcc siege gcc-c++ && sudo curl -Lo /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && sudo chmod a+x /usr/bin/jq

RUN wget -O /tmp/mandrel.tar.gz https://github.com/graalvm/mandrel/releases/download/mandrel-${MANDREL_VERSION}/mandrel-java11-linux-amd64-${MANDREL_VERSION}.tar.gz && cd /usr/local && tar -xvzf /tmp/mandrel.tar.gz && rm -rf /tmp/mandrel.tar.gz

USER jboss

RUN mkdir /home/jboss/.m2

COPY settings.xml /home/jboss/.m2

RUN cd /tmp && mkdir project && cd project && mvn io.quarkus:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -Dextensions="quarkus-resteasy-reactive,quarkus-resteasy-reactive-jackson,quarkus-agroal,quarkus-hibernate-orm,quarkus-hibernate-orm-panache,quarkus-jdbc-h2,quarkus-jdbc-postgresql,quarkus-kubernetes,quarkus-scheduler,quarkus-smallrye-fault-tolerance,quarkus-smallrye-health,quarkus-smallrye-opentracing" && mvn -f footest clean compile package && cd / && rm -rf /tmp/project

RUN cd /tmp && mkdir project && cd project && mvn io.quarkus:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -Dextensions="quarkus-smallrye-reactive-messaging,quarkus-smallrye-reactive-messaging-kafka,quarkus-vertx,quarkus-kafka-client,quarkus-micrometer-registry-prometheus,quarkus-smallrye-openapi,quarkus-qute,quarkus-resteasy-reactive-qute,quarkus-opentelemetry,quarkus-opentelemetry-exporter-jaeger" && mvn -f footest clean compile package -Pnative && cd / && rm -rf /tmp/project

RUN cd /tmp && git clone https://github.com/RedHat-Middleware-Workshops/cloud-native-workshop-v2-labs-solutions && cd cloud-native-workshop-v2-labs-solutions && git checkout ocp-${OC_VERSION} && cd m4 && for proj in *-service ; do mvn -fn -f ./$proj dependency:resolve-plugins dependency:resolve dependency:go-offline clean compile -DskipTests ; done && cd /tmp && rm -rf /tmp/cloud-native-workshop-v2-labs-solutions

RUN siege && sed -i 's/^connection = close/connection = keep-alive/' $HOME/.siege/siege.conf && sed -i 's/^benchmark = false/benchmark = true/' $HOME/.siege/siege.conf

RUN echo '-w "\n"' > $HOME/.curlrc

USER root
RUN chown -R jboss /home/jboss/.m2
RUN chmod -R a+w /home/jboss/.m2
RUN chmod -R a+rwx /home/jboss/.siege
RUN chown -R jboss /tmp/vertx-cache
RUN chmod -R a+w /tmp/vertx-cache
RUN chown -R jboss /tmp/quarkus
RUN chmod -R a+w /tmp/quarkus

USER jboss