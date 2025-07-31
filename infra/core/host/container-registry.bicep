@description('Container registry name')
param name string

@description('Location for the container registry')
param location string = resourceGroup().location

@description('Tags to apply to the container registry')
param tags object = {}

@description('Container registry SKU')
param sku string = 'Basic'

@description('Enable admin user')
param adminUserEnabled bool = false

@description('Principal ID of the managed identity')
param principalId string

resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-11-01-preview' = {
  name: name
  location: location
  tags: tags
  sku: {
    name: sku
  }
  properties: {
    adminUserEnabled: adminUserEnabled
    publicNetworkAccess: 'Enabled'
    zoneRedundancy: 'Disabled'
  }
}

// Grant AcrPull role to the managed identity
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, principalId, '7f951dda-4ed3-4680-a7ca-43fe172d538d')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

@description('Container registry name')
output name string = containerRegistry.name

@description('Container registry ID')
output id string = containerRegistry.id

@description('Container registry login server')
output loginServer string = containerRegistry.properties.loginServer
