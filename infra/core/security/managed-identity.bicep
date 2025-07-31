@description('Name of the managed identity')
param name string

@description('Location for the managed identity')
param location string = resourceGroup().location

@description('Tags to apply to the managed identity')
param tags object = {}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: name
  location: location
  tags: tags
}

@description('ID of the managed identity')
output id string = managedIdentity.id

@description('Name of the managed identity')
output name string = managedIdentity.name

@description('Principal ID of the managed identity')
output principalId string = managedIdentity.properties.principalId

@description('Client ID of the managed identity')
output clientId string = managedIdentity.properties.clientId
