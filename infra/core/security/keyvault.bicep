@description('Key Vault name')
param name string

@description('Location for Key Vault')
param location string = resourceGroup().location

@description('Tags to apply to Key Vault')
param tags object = {}

@description('SKU for the Key Vault')
param sku string = 'standard'

@description('Principal ID of the managed identity')
param principalId string

@description('Enable RBAC authorization')
param enableRbacAuthorization bool = true

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      family: 'A'
      name: sku
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: enableRbacAuthorization
    enableSoftDelete: true
    softDeleteRetentionInDays: 90
    enablePurgeProtection: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      bypass: 'AzureServices'
    }
  }
}

// Grant Key Vault Secrets Officer role to the managed identity
resource keyVaultRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, principalId, 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'b86a8fe4-44ce-4948-aee5-eccb2c155cd7') // Key Vault Secrets Officer
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

@description('Key Vault name')
output name string = keyVault.name

@description('Key Vault ID')
output id string = keyVault.id

@description('Key Vault URI')
output vaultUri string = keyVault.properties.vaultUri
