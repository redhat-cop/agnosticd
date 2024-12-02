#
# Create attestation predicate for RHTAP Jenkins builds
#
# Useful references:
# - https://slsa.dev/spec/v1.0/provenance
# - https://www.jenkins.io/doc/book/pipeline/jenkinsfile/#using-environment-variables
# - http://localhost:8080/env-vars.html/
#   (Replace localhost with your Jenkins instance)
#
yq -o=json -I=0 << EOT
---
buildDefinition:
  buildType: "https://redhat.com/rhtap/slsa-build-types/${CI_TYPE}-build/v1"
  externalParameters: {}
  internalParameters: {}
  resolvedDependencies:
    - uri: "git+${GIT_URL}"
      digest:
        gitCommit: "${GIT_COMMIT}"

runDetails:
  builder:
    id: "${NODE_NAME}"
    builderDependencies: []
    version:
      # Not sure if this is the right place for these...
      buildNumber: "${BUILD_NUMBER}"
      jobName: "${JOB_NAME}"
      executorNumber: "${EXECUTOR_NUMBER}"
      jenkinsHome: "${JENKINS_HOME}"
      buildUrl: "${BUILD_URL}"
      jobUrl: "${JOB_URL}"

  metadata:
    invocationID: "${BUILD_TAG}"
    startedOn: "$(cat $RESULTS/init/START_TIME)"
    # Inaccurate, but maybe close enough
    finishedOn: "$(date +%Y-%m-%dT%H:%M:%SZ)"

  byproducts:
    - name: SBOM_BLOB
      uri: "$(cat "$RESULTS/SBOM_BLOB_URL)"

EOT