# Accelerate New App Development

* https://docs.google.com/document/d/1QPm-oIsIGJVD3KPRvdCO4d64RZffDno-IXctkBWxkCU/edit
* https://docs.google.com/presentation/d/1ps1ot2qOc41K4TfDYvSbjzbhoSmRX-76K-XcXC17SSQ/edit

## Diagnosis steps after provisioning

```shell
oc get co
oc get nodes
oc get pipelinerun -A | grep Failed
oc get pipelinerun -A | grep Succeeded | wc -l
oc get taskrun -A | grep Failed
oc get pods -A | grep -v Running | grep -v Completed
```

## Trigger pipelines

In case the quarkus-pipeline failed.

```
tkn pipeline start quarkus-pipeline --workspace name=app-source,claimName=workspace-app-source --workspace name=maven-settings,emptyDir= --use-param-defaults -n tekton-userX
```

## Trigger tasks

In case the update-swagger task failed.

```
export GUID=65dr9
export SANDBOX=sandbox467
export OCP_USER=user5

tkn task start update-swagger \
--param restFightsOpenapiServers="http:\/\/rest-fights-quarkus-superheroes-${OCP_USER}.apps.cluster-${GUID}.${SANDBOX}.opentlc.com" \
--param restHeroesOpenapiServers="http:\/\/rest-heores-quarkus-superheroes-${OCP_USER}.apps.cluster-${GUID}.${SANDBOX}.opentlc.com" \
--param restVillainsOpenapiServers="http:\/\/rest-villains-quarkus-superheroes-${OCP_USER}.apps.cluster-${GUID}.${SANDBOX}.opentlc.com" \
--use-param-defaults --showlog -n tekton-${OCP_USER}

# ArgoCD needs to refresh and sync before deployment restart

oc rollout restart deploy rest-fights -n quarkus-superheroes-${OCP_USER}
```

## Redeploy lab guides

```shell
oc -n guides start-build acc-new-app-dev-m1 --follow
oc -n guides scale deployment acc-new-app-dev-m1 --replicas=0
oc -n guides scale deployment acc-new-app-dev-m1 --replicas=1
```
