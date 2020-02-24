# syntax = docker/dockerfile:experimental

# To build this stack:
# Put your Red Hat Developer credentials in rhsm.secret.yaml file in this same directory, whose contents should be:
# RH_USERNAME=your-username
# RH_PASSWORD=your-password
#
# then:
# DOCKER_BUILDKIT=1 docker build --progress=plain --secret id=rhsm,src=rhsm.secret.yaml -t quay.io/username/cloudnative-workspaces-quarkus:VVV -f stack.Dockerfile .
# docker push quay.io/username/quay.io/username/cloudnative-workspaces-quarkus:VVVV

FROM registry.redhat.io/codeready-workspaces/stacks-java-rhel8:2.0

ENV GRAALVM_VERSION=19.3.1
ENV QUARKUS_VERSION=1.2.0.Final
ENV MVN_VERSION=3.6.3
ENV GRAALVM_HOME="/usr/local/graalvm-ce-java8-${GRAALVM_VERSION}"
ENV MAVEN_OPTS="-Xmx4G -Xss128M -XX:MetaspaceSize=1G -XX:MaxMetaspaceSize=2G -XX:+CMSClassUnloadingEnabled"
ENV PATH="/usr/local/maven/apache-maven-${MVN_VERSION}/bin:${PATH}"

USER root

RUN wget -O /tmp/oc.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/oc/4.3/linux/oc.tar.gz && cd /usr/bin && tar -xvzf /tmp/oc.tar.gz && chmod a+x /usr/bin/oc && rm -f /tmp/oc.tar.gz

RUN wget -O /tmp/kn.tar.gz https://mirror.openshift.com/pub/openshift-v4/clients/serverless/0.11.0/kn-linux-amd64-0.11.0.tar.gz && cd /usr/bin && tar -xvzf /tmp/kn.tar.gz ./kn && chmod a+x kn && rm -f /tmp/kn.tar.gz

RUN wget -O /tmp/tkn.tar.gz https://github.com/tektoncd/cli/releases/download/v0.7.1/tkn_0.7.1_Linux_x86_64.tar.gz && cd /usr/bin && tar -xvzf /tmp/tkn.tar.gz tkn&& chmod a+x tkn && rm -f /tmp/tkn.tar.gz

RUN wget -O /tmp/graalvm.tar.gz https://github.com/graalvm/graalvm-ce-builds/releases/download/vm-${GRAALVM_VERSION}/graalvm-ce-java8-linux-amd64-${GRAALVM_VERSION}.tar.gz && cd /usr/local && tar -xvzf /tmp/graalvm.tar.gz && rm -rf /tmp/graalvm.tar.gz && ${GRAALVM_HOME}/bin/gu install native-image

RUN wget -O /tmp/mvn.tar.gz https://www-us.apache.org/dist/maven/maven-3/${MVN_VERSION}/binaries/apache-maven-${MVN_VERSION}-bin.tar.gz && tar xzf /tmp/mvn.tar.gz && rm -rf /tmp/mvn.tar.gz && mkdir /usr/local/maven && mv apache-maven-${MVN_VERSION}/ /usr/local/maven/ && alternatives --install /usr/bin/mvn mvn /usr/local/maven/apache-maven-${MVN_VERSION}/bin/mvn 1

RUN --mount=type=secret,id=rhsm username="$(grep RH_USERNAME /run/secrets/rhsm|cut -d= -f2)" && password="$(grep RH_PASSWORD /run/secrets/rhsm|cut -d= -f2)" && subscription-manager register --username $username --password $password --auto-attach && yum install -y gcc zlib-devel && yum install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && yum install -y siege jq && subscription-manager remove --all && subscription-manager unregister

USER jboss

RUN cd /tmp && mkdir project && cd project && mvn io.quarkus:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -Dextensions="quarkus-agroal,quarkus-arc,quarkus-hibernate-orm,quarkus-hibernate-orm-panache,quarkus-jdbc-h2,quarkus-jdbc-postgresql,quarkus-kubernetes,quarkus-scheduler,quarkus-smallrye-fault-tolerance,quarkus-smallrye-health,quarkus-smallrye-opentracing" && mvn -f footest clean compile package && cd / && rm -rf /tmp/project

RUN cd /tmp && mkdir project && cd project && mvn io.quarkus:quarkus-maven-plugin:${QUARKUS_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -Dextensions="quarkus-smallrye-reactive-streams-operators,quarkus-smallrye-reactive-messaging,quarkus-smallrye-reactive-messaging-kafka,quarkus-swagger-ui,quarkus-vertx,quarkus-kafka-client, quarkus-smallrye-metrics,quarkus-smallrye-openapi" && mvn -f footest clean compile package -Pnative && cd / && rm -rf /tmp/project

RUN siege && sed -i 's/^connection = close/connection = keep-alive/' $HOME/.siege/siege.conf && sed -i 's/^benchmark = false/benchmark = true/' $HOME/.siege/siege.conf

RUN echo '-w "\n"' > $HOME/.curlrc

USER root
RUN chown -R jboss /home/jboss/.m2
RUN chmod -R a+w /home/jboss/.m2
USER jboss
