@description('Key Vault name')
param keyVaultName string

@description('Key Vault secrets to create')
param secrets array = []

resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' existing = {
  name: keyVaultName
}

resource keyVaultSecrets 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = [for secret in secrets: {
  name: secret.name
  parent: keyVault
  properties: {
    value: secret.value
    contentType: secret.?contentType ?? 'text/plain'
  }
}]

@description('Created secret names')
output secretNames array = [for (secret, i) in secrets: keyVaultSecrets[i].name]
