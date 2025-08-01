@description('Storage account name')
param name string

@description('Location for the storage account')
param location string = resourceGroup().location

@description('Tags to apply to the storage account')
param tags object = {}

@description('Storage account SKU')
param sku object = {
  name: 'Standard_LRS'
}

@description('Allow blob public access')
param allowBlobPublicAccess bool = false

@description('Allow nested items to be public')
param allowNestedItemsToBePublic bool = false

@description('Default action for network rules')
param networkRuleSetDefaultAction string = 'Allow'

@description('Container names to create')
param containers array = []

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: name
  location: location
  tags: tags
  kind: 'StorageV2'
  sku: sku
  properties: {
    accessTier: 'Hot'
    allowBlobPublicAccess: allowBlobPublicAccess
    allowCrossTenantReplication: false
    allowSharedKeyAccess: true
    defaultToOAuthAuthentication: false
    isHnsEnabled: false
    isNfsV3Enabled: false
    isSftpEnabled: false
    minimumTlsVersion: 'TLS1_2'
    networkAcls: {
      defaultAction: networkRuleSetDefaultAction
    }
    publicNetworkAccess: 'Enabled'
    supportsHttpsTrafficOnly: true
  }
}

resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-05-01' = if (length(containers) > 0) {
  name: 'default'
  parent: storageAccount
  properties: {
    deleteRetentionPolicy: {
      enabled: false
    }
    cors: {
      corsRules: [
        {
          allowedOrigins: ['*']
          allowedMethods: ['GET', 'HEAD', 'OPTIONS']
          allowedHeaders: ['*']
          exposedHeaders: ['*']
          maxAgeInSeconds: 3600
        }
      ]
    }
  }
}

resource storageContainers 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-05-01' = [for container in containers: {
  name: container
  parent: blobServices
  properties: {
    publicAccess: 'None' // Keep private, we'll use SAS tokens or authenticated access
  }
}]

@description('Storage account name')
output name string = storageAccount.name

@description('Storage account ID')
output id string = storageAccount.id

@description('Storage account primary endpoints')
output primaryEndpoints object = storageAccount.properties.primaryEndpoints

@description('Storage account primary key')
output primaryKey string = storageAccount.listKeys().keys[0].value

@description('Storage account connection string')
output connectionString string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccount.listKeys().keys[0].value};EndpointSuffix=${environment().suffixes.storage}'
