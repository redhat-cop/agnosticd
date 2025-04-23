@description('Location')
param location string = resourceGroup().location

@description('Domain Prefix')
param domain string

@description('Version of the OpenShift cluster')
param version string

@description('Pull secret from cloud.redhat.com. The json should be input as a string')
@secure()
param pullSecret string = ''

@description('Name of ARO vNet')
param clusterVnetName string

@description('ARO vNet Address Space')
param clusterVnetCidr string = '10.100.0.0/15'

@description('Worker node subnet address space')
param workerSubnetCidr string = '10.100.70.0/23'

@description('Master node subnet address space')
param masterSubnetCidr string = '10.100.76.0/24'

@description('Master Node VM Type')
param masterVmSize string = 'Standard_D8s_v3'

@description('Worker Node VM Type')
param workerVmSize string = 'Standard_D4s_v3'

@description('Worker Node Disk Size in GB')
@minValue(128)
param workerVmDiskSize int = 128

@description('Cidr for Pods')
param podCidr string = '10.128.0.0/14'

@metadata({
 description: 'Cidr of service'
})
param serviceCidr string = '172.30.0.0/16'

@description('Unique name for the cluster')
param clusterName string

@description('Api Server Visibility')
@allowed([
 'Private'
 'Public'
])
param apiServerVisibility string = 'Public'

@description('Ingress Visibility')
@allowed([
 'Private'
 'Public'
])
param ingressVisibility string = 'Public'

@description('The ObjectID of the Resource Provider Service Principal')
param rpObjectId string

@description('Specify if FIPS validated crypto modules are used')
@allowed([
 'Enabled'
 'Disabled'
])
param fips string = 'Disabled'

@description('Specify if master VMs are encrypted at host')
@allowed([
 'Enabled'
 'Disabled'
])
param masterEncryptionAtHost string = 'Disabled'

@description('Specify if worker VMs are encrypted at host')
@allowed([
 'Enabled'
 'Disabled'
])
param workerEncryptionAtHost string = 'Disabled'

var resourceGroupId = '/subscriptions/${subscription().subscriptionId}/resourceGroups/aro-${domain}-${location}'
var masterSubnetId=resourceId('Microsoft.Network/virtualNetworks/subnets', clusterVnetName, 'master')
var workerSubnetId=resourceId('Microsoft.Network/virtualNetworks/subnets', clusterVnetName, 'worker')

resource vnet 'Microsoft.Network/virtualNetworks@2023-06-01' = {
 name: clusterVnetName
 location: location
 properties: {
   addressSpace: { addressPrefixes: [ clusterVnetCidr ] }
   subnets: [
     {
       name: 'master'
       properties: {
         addressPrefixes: [ masterSubnetCidr ]
         serviceEndpoints: [ { service: 'Microsoft.ContainerRegistry' } ]
       }
     }
     {
       name: 'worker'
       properties: {
         addressPrefixes: [ workerSubnetCidr ]
         serviceEndpoints: [ { service: 'Microsoft.ContainerRegistry' } ]
       }
     }
   ]
 }
}

resource workerSubnet 'Microsoft.Network/virtualNetworks/subnets@2020-08-01' existing = {
 parent: vnet
 name: 'worker'
}

resource masterSubnet 'Microsoft.Network/virtualNetworks/subnets@2020-08-01' existing = {
 parent: vnet
 name: 'master'
}

// create required identities

resource cloudControllerManager 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'cloud-controller-manager'
   location: location
}

resource ingress 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'ingress'
   location: location
}

resource machineApi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'machine-api'
   location: location
}

resource diskCsiDriver 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'disk-csi-driver'
   location: location
}

resource cloudNetworkConfig 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'cloud-network-config'
   location: location
}

resource imageRegistry 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'image-registry'
   location: location
}

resource fileCsiDriver 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'file-csi-driver'
   location: location
}

resource aroOperator 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'aro-operator'
   location: location
}

resource clusterMsi 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
   name: 'cluster'
   location: location
}

// create required role assignments on vnet / subnets

resource cloudControllerManagerMasterSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(masterSubnet.id, 'cloud-controller-manager')
   scope: masterSubnet
   properties: {
       principalId: cloudControllerManager.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a1f96423-95ce-4224-ab27-4e3dc72facd4')
       principalType: 'ServicePrincipal'
   }
}

resource cloudControllerManagerWorkerSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
 name: guid(workerSubnet.id, 'cloud-controller-manager')
 scope: workerSubnet
 properties: {
     principalId: cloudControllerManager.properties.principalId
     roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'a1f96423-95ce-4224-ab27-4e3dc72facd4')
     principalType: 'ServicePrincipal'
 }
}

resource ingressMasterSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(masterSubnet.id, 'ingress')
   scope: masterSubnet
   properties: {
       principalId: ingress.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0336e1d3-7a87-462b-b6db-342b63f7802c')
       principalType: 'ServicePrincipal'
   }
}

resource ingressWorkerSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
 name: guid(workerSubnet.id, 'ingress')
 scope: workerSubnet
 properties: {
     principalId: ingress.properties.principalId
     roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0336e1d3-7a87-462b-b6db-342b63f7802c')
     principalType: 'ServicePrincipal'
 }
}

resource machineApiMasterSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(masterSubnet.id, 'machine-api')
   scope: masterSubnet
   properties: {
       principalId: machineApi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0358943c-7e01-48ba-8889-02cc51d78637')
       principalType: 'ServicePrincipal'
   }
}

resource machineApiWorkerSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(workerSubnet.id, 'machine-api')
   scope: workerSubnet
   properties: {
       principalId: machineApi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0358943c-7e01-48ba-8889-02cc51d78637')
       principalType: 'ServicePrincipal'
   }
}

resource cloudNetworkConfigVnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(vnet.id, 'cloud-network-config')
   scope: vnet
   properties: {
       principalId: cloudNetworkConfig.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'be7a6435-15ae-4171-8f30-4a343eff9e8f')
       principalType: 'ServicePrincipal'
   }
}

resource fileCsiDriverMasterSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(masterSubnet.id, 'file-csi-driver')
   scope: masterSubnet
   properties: {
       principalId: fileCsiDriver.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0d7aedc0-15fd-4a67-a412-efad370c947e')
       principalType: 'ServicePrincipal'
   }
}

resource fileCsiDriverWorkerSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
 name: guid(workerSubnet.id, 'file-csi-driver')
 scope: workerSubnet
 properties: {
     principalId: fileCsiDriver.properties.principalId
     roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0d7aedc0-15fd-4a67-a412-efad370c947e')
     principalType: 'ServicePrincipal'
 }
}

resource aroOperatorMasterSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(masterSubnet.id, 'aro-operator')
   scope: masterSubnet
   properties: {
       principalId: aroOperator.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4436bae4-7702-4c84-919b-c4069ff25ee2')
       principalType: 'ServicePrincipal'
   }
}

resource aroOperatorWorkerSubnetRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
 name: guid(workerSubnet.id, 'aro-operator')
 scope: workerSubnet
 properties: {
     principalId: aroOperator.properties.principalId
     roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4436bae4-7702-4c84-919b-c4069ff25ee2')
     principalType: 'ServicePrincipal'
 }
}

// create required role assignments on cluster MSI

resource clusterMsiRoleAssignmentCloudControllerManager 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(cloudControllerManager.id, 'cluster')
   scope: cloudControllerManager
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

resource clusterMsiRoleAssignmentIngress 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(ingress.id, 'cluster')
   scope: ingress
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

resource clusterMsiRoleAssignmentMachineApi 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(machineApi.id, 'cluster')
   scope: machineApi
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

resource clusterMsiRoleAssignmentDiskCsiDriver 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(diskCsiDriver.id, 'cluster')
   scope: diskCsiDriver
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

resource clusterMsiRoleAssignmentCloudNetworkConfig 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(cloudNetworkConfig.id, 'cluster')
   scope: cloudNetworkConfig
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

resource clusterMsiRoleAssignmentCloudImageRegistry 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(imageRegistry.id, 'cluster')
   scope: imageRegistry
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

resource clusterMsiRoleAssignmentCloudFileCsiDriver 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(fileCsiDriver.id, 'cluster')
   scope: fileCsiDriver
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

resource clusterMsiRoleAssignmentCloudAroOperator 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(aroOperator.id, 'cluster')
   scope: aroOperator
   properties: {
       principalId: clusterMsi.properties.principalId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ef318e2a-8334-4a05-9e4a-295a196c6a6e')
       principalType: 'ServicePrincipal'
   }
}

// create first party role assignment over the vnet

resource fpspRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
   name: guid(vnet.id, rpObjectId)
   scope: vnet
   properties: {
       principalId: rpObjectId
       roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4d97b98b-1d4f-4787-a291-c67834d212e7')
       principalType: 'ServicePrincipal'
   }
}

// create cluster

resource cluster 'Microsoft.RedHatOpenShift/openShiftClusters@2024-08-12-preview' = {
   name: clusterName
   location: location
   properties: {
       clusterProfile: {
           domain: domain
           #disable-next-line use-resource-id-functions
           resourceGroupId: resourceGroupId
           version: version
           fipsValidatedModules: fips
           pullSecret: pullSecret
       }
       networkProfile: {podCidr: podCidr, serviceCidr: serviceCidr}
       masterProfile: {
           vmSize: masterVmSize
           subnetId: masterSubnetId
           encryptionAtHost: masterEncryptionAtHost
       }
       workerProfiles: [{
           name: 'worker'
           count: 3
           diskSizeGB: workerVmDiskSize
           vmSize: workerVmSize
           subnetId: workerSubnetId
           encryptionAtHost: workerEncryptionAtHost
       }]
       apiserverProfile: {visibility: apiServerVisibility}
       ingressProfiles: [{name: 'default', visibility: ingressVisibility}]
       platformWorkloadIdentityProfile: {
           platformWorkloadIdentities: {
               'cloud-controller-manager': {resourceId: cloudControllerManager.id}
               ingress: {resourceId: ingress.id}
               'machine-api': {resourceId: machineApi.id}
               'disk-csi-driver': {resourceId: diskCsiDriver.id}
               'cloud-network-config': {resourceId: cloudNetworkConfig.id}
               'image-registry': {resourceId: imageRegistry.id}
               'file-csi-driver': {resourceId: fileCsiDriver.id}
               'aro-operator': {resourceId: aroOperator.id}
           }
       }
   }
   identity: {
       type: 'UserAssigned'
       userAssignedIdentities: {
           '${clusterMsi.id}': {}
       }
   }
}