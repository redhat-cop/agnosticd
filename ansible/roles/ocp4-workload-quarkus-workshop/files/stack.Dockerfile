# To build this stack:
# docker build -t quay.io/openshiftlabs/quarkus-workshop-stack:3.20-4.19.7 -f stack.Dockerfile .
# docker push quay.io/openshiftlabs/quarkus-workshop-stack:3.20-4.19.7
# macOS M1: --platform linux/x86_64

FROM registry.redhat.io/devspaces/udi-rhel9:latest

ENV MANDREL_VERSION=23.1.2.0-Final
ENV MVN_VERSION=3.9.6
ENV GRAALVM_HOME="/usr/local/mandrel-java21-${MANDREL_VERSION}"
ENV JAVA_HOME="/usr/lib/jvm/java-21-openjdk" 
ENV PATH="/usr/local/maven/apache-maven-${MVN_VERSION}/bin:$JAVA_HOME/bin:${PATH}"
ENV RHBQ_VERSION=3.20.1.redhat-00003
ENV QUARKUS_CLI_VERSION=3.24.3
ENV JBANG_DIR="/usr/local/jbang"
ENV OC_VERSION=4.19.7

USER root

# WARNING: devspaces/udi-rhel9 also provides an oc binary!
# Run the following oc installation ONLY in cases when a custom oc version is required:
RUN curl -s https://mirror.openshift.com/pub/openshift-v4/clients/ocp/$OC_VERSION/openshift-client-linux-$OC_VERSION.tar.gz -o /tmp/openshift-client-linux-$OC_VERSION.tar.gz && tar -xvf /tmp/openshift-client-linux-$OC_VERSION.tar.gz -C /usr/bin/ && chmod +x /usr/bin/oc && chmod +x /usr/bin/kubectl && rm /tmp/openshift-client-linux-$OC_VERSION.tar.gz /usr/bin/README.md
# RUN wget -O /tmp/openjdk-21.0.7.tar.gz https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.7%2B6/OpenJDK21U-jdk_x64_linux_hotspot_21.0.7_6.tar.gz && tar -xvzf /tmp/openjdk-21.0.7.tar.gz && rm -rf /tmp/openjdk-21.0.7.tar.gz && mv jdk-21.0.7+6 /tmp/java-21-openjdk && sudo mv /tmp/java-21-openjdk /usr/lib/jvm/ && sudo alternatives --install /usr/bin/java java /usr/lib/jvm/java-21-openjdk/bin/java 1
RUN wget -O /tmp/mvn.tar.gz https://archive.apache.org/dist/maven/maven-3/${MVN_VERSION}/binaries/apache-maven-${MVN_VERSION}-bin.tar.gz && sudo tar -xvzf /tmp/mvn.tar.gz && rm -rf /tmp/mvn.tar.gz && mkdir /usr/local/maven && mv apache-maven-${MVN_VERSION}/ /usr/local/maven/ && alternatives --install /usr/bin/mvn mvn /usr/local/maven/apache-maven-${MVN_VERSION}/bin/mvn 1
RUN sudo rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-8.noarch.rpm && sudo microdnf install -y zlib-devel gcc siege gcc-c++ && sudo curl -Lo /usr/bin/jq https://github.com/stedolan/jq/releases/download/jq-1.6/jq-linux64 && sudo chmod a+x /usr/bin/jq
RUN wget -O /tmp/mandrel.tar.gz https://github.com/graalvm/mandrel/releases/download/mandrel-${MANDREL_VERSION}/mandrel-java21-linux-amd64-${MANDREL_VERSION}.tar.gz && cd /usr/local && sudo tar -xvzf /tmp/mandrel.tar.gz && rm -rf /tmp/mandrel.tar.gz
RUN ln -f -s /usr/lib/jvm/java-21-openjdk/* ${HOME}/.java/current

RUN mkdir -p /usr/local/quarkus-cli/lib && mkdir /usr/local/quarkus-cli/bin
RUN wget -O /tmp/quarkus-cli.tgz https://github.com/quarkusio/quarkus/releases/download/${QUARKUS_CLI_VERSION}/quarkus-cli-${QUARKUS_CLI_VERSION}.tar.gz && tar -xzf /tmp/quarkus-cli.tgz -C /tmp
RUN cp /tmp/quarkus-cli-${QUARKUS_CLI_VERSION}/bin/quarkus /usr/local/bin && cp /tmp/quarkus-cli-${QUARKUS_CLI_VERSION}/lib/quarkus-cli-${QUARKUS_CLI_VERSION}-runner.jar /usr/local/lib
RUN chmod +x /usr/local/bin/quarkus && cd /usr/local/bin
RUN mkdir -p ${JBANG_DIR} && curl -Ls https://sh.jbang.dev | bash -s - app setup 
RUN ln -s ${JBANG_DIR}/bin/jbang /usr/local/bin/jbang

USER user

RUN mkdir -p /home/user/.m2
COPY settings.xml /home/user/.m2
RUN cd /tmp && mkdir project && cd project && mvn com.redhat.quarkus.platform:quarkus-maven-plugin:${RHBQ_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -DplatformGroupId=com.redhat.quarkus.platform -DplatformVersion=${RHBQ_VERSION} -Dextensions="quarkus-rest,quarkus-rest-jackson,quarkus-agroal,quarkus-jdbc-h2,quarkus-jdbc-postgresql,quarkus-kubernetes,quarkus-scheduler,quarkus-smallrye-fault-tolerance,quarkus-smallrye-health" && mvn -f footest clean compile package -DskipTests && cd / && rm -rf /tmp/project
RUN cd /tmp && mkdir project && cd project && mvn com.redhat.quarkus.platform:quarkus-maven-plugin:${RHBQ_VERSION}:create -DprojectGroupId=org.acme -DprojectArtifactId=footest -DplatformGroupId=com.redhat.quarkus.platform -DplatformVersion=${RHBQ_VERSION} -Dextensions="quarkus-messaging-kafka,quarkus-vertx,quarkus-kafka-client,quarkus-micrometer-registry-prometheus,quarkus-smallrye-openapi,quarkus-rest-qute,quarkus-opentelemetry" && mvn -f footest clean compile package -Pnative -DskipTests && cd / && rm -rf /tmp/project
RUN cd /tmp && git clone https://github.com/RedHat-Middleware-Workshops/quarkus-workshop-m3-labs && cd quarkus-workshop-m3-labs && git checkout ocp-4.19 && for proj in *-petclinic* ; do mvn -fn -f ./$proj dependency:resolve-plugins dependency:resolve dependency:go-offline clean compile -DskipTests ; done && cd /tmp && rm -rf /tmp/quarkus-workshop-m3-labs
RUN siege && sed -i 's/^connection = close/connection = keep-alive/' $HOME/.siege/siege.conf && sed -i 's/^benchmark = false/benchmark = true/' $HOME/.siege/siege.conf
RUN echo '-w "\n"' > $HOME/.curlrc

USER root
RUN chown -R user /home/user/.m2
RUN chmod -R a+w /home/user/.m2
RUN chmod -R a+rwx /home/user/.siege

USER user
