for i in `oc get clusterroles | grep istio`; do
    oc delete clusterrole $i;
done

for i in `oc get customresourcedefinitions | grep istio | awk '{print $1}'`; do
    oc delete customresourcedefinitions $i;
done
