# To build this stack:
# docker build -t quay.io/username/quarkus-workshop-stack:VVV -f stack.Dockerfile .
# docker push quay.io/username/quarkus-workshop-stack:VVVV
# macOS M1: --platform linux/x86_64

FROM registry.redhat.io/devspaces/udi-rhel8:latest

ENV MANDREL_VERSION=22.3.1.0-Final
ENV QUARKUS_VERSION=2.13.7.Final-redhat-00003
ENV OC_VERSION=4.12
ENV MVN_VERSION=3.8.4
ENV GRAALVM_HOME="/usr/local/mandrel-java17-${MANDREL_VERSION}"
ENV PATH="/usr/local/maven/apache-maven-${MVN_VERSION}/bin:${PATH}"
ENV JAVA_HOME=$JAVA_HOME_17

USER root

RUN wget -O /tmp/mvn.tar.gz https://archive.apache.org/dist/maven/maven-3/${MVN_VERSION}/binaries/apache-maven-${MVN_VERSION}-bin.tar.gz && sudo tar -xvzf /tmp/mvn.tar.gz && rm -rf /tmp/mvn.tar.gz && mkdir /usr/local/maven && mv apache-maven-${MVN_VERSION}/ /usr/local/maven/ && alternatives --install /usr/bin/mvn mvn /usr/local/maven/apache-maven-${MVN_VERSION}/bin/mvn 1

RUN wget -O /tmp/oc.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/ocp/${OC_VERSION}.3/openshift-client-linux-${OC_VERSION}.3.tar.gz && cd /usr/bin && sudo tar -xvzf /tmp/oc.tar.gz && sudo chmod a+x /usr/bin/oc && rm -f /tmp/oc.tar.gz

RUN sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && sudo microdnf install -y zlib-devel gcc siege gcc-c++ && sudo curl -Lo /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && sudo chmod a+x /usr/bin/jq

RUN wget -O /tmp/mandrel.tar.gz https://github.com/graalvm/mandrel/releases/download/mandrel-${MANDREL_VERSION}/mandrel-java17-linux-amd64-${MANDREL_VERSION}.tar.gz && cd /usr/local && sudo tar -xvzf /tmp/mandrel.tar.gz && rm -rf /tmp/mandrel.tar.gz

RUN ln -f -s /usr/lib/jvm/java-17-openjdk/* ${HOME}/.java/current

USER user

RUN mkdir -p /home/user/.m2

COPY settings.xml /home/user/.m2

RUN cd /tmp && mkdir project && cd project && mvn com.redhat.quarkus.platform:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -DplatformGroupId=com.redhat.quarkus.platform -DplatformVersion=${QUARKUS_VERSION} -Dextensions="quarkus-resteasy-reactive,quarkus-resteasy-reactive-jackson,quarkus-agroal,quarkus-hibernate-orm,quarkus-hibernate-orm-panache,quarkus-hibernate-reactive-panache,quarkus-jdbc-h2,quarkus-jdbc-postgresql,quarkus-kubernetes,quarkus-scheduler,quarkus-smallrye-fault-tolerance,quarkus-smallrye-health,quarkus-smallrye-opentracing" && mvn -f footest clean compile package -DskipTests && cd / && rm -rf /tmp/project

RUN cd /tmp && mkdir project && cd project && mvn com.redhat.quarkus.platform:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -DplatformGroupId=com.redhat.quarkus.platform -DplatformVersion=${QUARKUS_VERSION} -Dextensions="quarkus-smallrye-reactive-messaging,quarkus-smallrye-reactive-messaging-kafka,quarkus-vertx,quarkus-kafka-client,quarkus-micrometer-registry-prometheus,quarkus-smallrye-openapi,quarkus-qute,quarkus-resteasy-reactive-qute,quarkus-opentelemetry,quarkus-opentelemetry-exporter-jaeger" && mvn -f footest clean compile package -Pnative -DskipTests && cd / && rm -rf /tmp/project

RUN cd /tmp && git clone https://github.com/RedHat-Middleware-Workshops/quarkus-workshop-m3-labs && cd quarkus-workshop-m3-labs && git checkout ocp-${OC_VERSION} && for proj in *-petclinic* ; do mvn -fn -f ./$proj dependency:resolve-plugins dependency:resolve dependency:go-offline clean compile -DskipTests ; done && cd /tmp && rm -rf /tmp/quarkus-workshop-m3-labs

RUN siege && sed -i 's/^connection = close/connection = keep-alive/' $HOME/.siege/siege.conf && sed -i 's/^benchmark = false/benchmark = true/' $HOME/.siege/siege.conf

RUN echo '-w "\n"' > $HOME/.curlrc

USER root
RUN chown -R user /home/user/.m2
RUN chmod -R a+w /home/user/.m2
RUN chmod -R a+rwx /home/user/.siege

USER user