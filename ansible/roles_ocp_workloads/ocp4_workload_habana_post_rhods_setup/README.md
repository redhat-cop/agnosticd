### Run this role post KMM, NFD and Habana Gaudi Accelerators / GPU Setup Role completion and RHODS operator installation role completion ###

# Once the role installation is comleted, update the respective notebook by adding       "habana.ai/gaudi: '1'" as shown below in limits and requests for the main container.
# With the release of RHODS 1.34, below procedure is not required.

# From UI - API Epxlorer, search for notebook. Select v1 with Group kubeflow.org & instances(Be sure to be in rhods-notebooks project or respective project where you are running the notebook). Go to instances , select your instance and edit the yaml file to add habana.ai/gaudi hpu's as shown below.

spec:
 template:
 spec:
 affinity:
 nodeAffinity:
 preferredDuringSchedulingIgnoredDuringExecution:
- preference:
 matchExpressions:
- key: nvidia.com/gpu.present
 operator: NotIn
 values:
- 'true'
 weight: 1
 containers:
- resources:
 limits:
 cpu: '2'
** habana.ai/gaudi: '1'
 memory: 8Gi
 requests:
 cpu: '1'
** habana.ai/gaudi: '1'
 memory: 8Gi