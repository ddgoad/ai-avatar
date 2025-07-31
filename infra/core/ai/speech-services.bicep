metadata description = 'Creates an Azure Cognitive Services Speech resource.'

@description('Name of the Azure Speech Services account.')
param name string

@description('Location for the Speech Services account.')
param location string = resourceGroup().location

@description('Tags to apply to the Speech Services account.')
param tags object = {}

@description('SKU for the Speech Services account.')
@allowed(['F0', 'S0'])
param sku string = 'S0'

@description('Managed identity principal ID for RBAC assignments.')
param managedIdentityPrincipalId string = ''

resource speechAccount 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'SpeechServices'
  sku: {
    name: sku
  }
  properties: {
    apiProperties: {}
    customSubDomainName: name
    networkAcls: {
      defaultAction: 'Allow'
    }
    publicNetworkAccess: 'Enabled'
  }
  identity: {
    type: 'SystemAssigned'
  }
}

// Output values
output id string = speechAccount.id
output name string = speechAccount.name
output endpoint string = speechAccount.properties.endpoint
output key string = speechAccount.listKeys().key1
output location string = speechAccount.location