# Gitops Bootstrap

## Update 2025-01-10

1. Health Check: Adds ability to wait for all gitops applications with a particular tag to be healthy and synced before continuing. @judd
1. Retrieve user_data, multiuser: reads special user_data configmaps to bring values into AgD agnosticd_user_info.data

## Pass values from bootstrap application back to AgD

`data.users_json:` is the key this workload looks for to import multi-user data

### Sample ConfigMap

    # Sample multi-user configmap
    # "data.users_json:" is what this workload looks for to import multi-user data
    apiVersion: v1
    data:
      users_json: '{"users": {"user1": { "kiali_url": "https://kiali-istio-system.apps.rosa-9gp6n.6jcc.p1.openshiftapps.com",
        "sample_first_key": "sample_first_value" },"user2": { "kiali_url": "https://kiali-istio-system.apps.rosa-9gp6n.6jcc.p1.openshiftapps.com",
        "sample_first_key": "sample_first_value" }}}'
      sample_global_value: "global_values"
      sample_global_yaml: |
        sample_global_yaml:
          sample_yaml_key: sample_yaml_value
    kind: ConfigMap
    metadata:
      labels:
        app.kubernetes.io/instance: uplift
        demo.redhat.com/userinfo: "" # required
      name: userinfo-users-json      # use any name
      namespace: istio-system        # use any ns
