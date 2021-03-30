FROM registry.access.redhat.com/fuse7/fuse-ignite-server:1.2-5

USER 0

COPY OpenShiftConfigurationProperties.class /tmp

RUN mkdir -p  /tmp/custom-syndesis/io/syndesis/server/openshift && \
    cp /tmp/OpenShiftConfigurationProperties.class /tmp/custom-syndesis/io/syndesis/server/openshift/ && \
    cp /deployments/runtime.jar /tmp/custom-syndesis && \
    cd /tmp/custom-syndesis && \
    jar xf runtime.jar BOOT-INF/lib/server-openshift-1.5.8.fuse-720001-redhat-00002.jar && \
    jar u0f BOOT-INF/lib/server-openshift-1.5.8.fuse-720001-redhat-00002.jar io/syndesis/server/openshift/OpenShiftConfigurationProperties.class && \
    jar u0f runtime.jar BOOT-INF/lib/server-openshift-1.5.8.fuse-720001-redhat-00002.jar && \
    cp /tmp/custom-syndesis/runtime.jar /deployments/

USER 185
