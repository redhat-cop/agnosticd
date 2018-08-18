# Download:
#   curl -o catalog-service-1.0.jar http://people.redhat.com/cdarby/rhte/msa-and-service-mesh/catalog-service-1.0.0-SNAPSHOT.jar

# Build:
#   docker build --rm -t catalog-service:1.0 -f Dockerfile.catalog .
#   docker tag catalog-service:1.0 docker.io/rhtgptetraining/catalog-service:1.0
#   docker push docker.io/rhtgptetraining/catalog-service:1.0

FROM fabric8/java-jboss-openjdk8-jdk:1.3.1
ENV JAVA_APP_DIR=/deployments
ENV AB_OFF=true
ENV JAEGER_SERVICE_NAME=catalog-service \
  JAEGER_PROPAGATION=b3 \
  JAEGER_SAMPLER_TYPE=const \
  JAEGER_SAMPLER_PARAM=1 \
  JAEGER_ENDPOINT=http://jaeger-collector.istio-system.svc:14268/api/traces 
EXPOSE 8080 8778 9779
COPY catalog-service-1.0.jar /deployments/catalog-service.jar
