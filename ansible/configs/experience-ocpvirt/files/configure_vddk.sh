cat << EOF | oc apply -f -
---
apiVersion: image.openshift.io/v1
kind: ImageStream
metadata:
  name: vddk
  namespace: openshift
EOF

cat << EOF | oc apply -f -
---
kind: BuildConfig
apiVersion: build.openshift.io/v1
metadata:
  name: vddk-build
  namespace: openshift
spec:
  output:
    to:
      kind: ImageStreamTag
      name: 'vddk:latest'
  strategy:
    type: Docker
    dockerStrategy:
      from:
        kind: ImageStreamTag
        namespace: openshift
        name: 'tools:latest'
  source:
    type: Dockerfile
    dockerfile: |
      FROM registry.access.redhat.com/ubi8/ubi-minimal 
      RUN curl -L -O www.opentlc.com/download/ocp4_baremetal/VMware-vix-disklib-7.0.3-20134304.x86_64.tar.gz
      RUN tar -xzf VMware-vix-disklib-7.0.3-20134304.x86_64.tar.gz
      RUN mkdir -p /opt
      ENTRYPOINT ["cp", "-r", "/vmware-vix-disklib-distrib", "/opt"]
  triggers:
  - type: ImageChange
    imageChange: {}
  - type: ConfigChange
EOF

sleep 10

oc -n openshift annotate is vddk test="$(date)"
