targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Azure OpenAI endpoint URL')
param azureOpenAIEndpoint string = ''

@description('Azure OpenAI API key')
@secure()
param azureOpenAIKey string = ''

@description('Container image for the web service')
param containerImage string = ''

// Resource naming following TDD specifications
var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Single resource group as specified in TDD
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: 'rg-aiavatar'
  location: location
  tags: tags
}

// User Assigned Managed Identity
module managedIdentity './core/security/managed-identity.bicep' = {
  name: 'managed-identity'
  scope: rg
  params: {
    name: '${abbrs.managedIdentityUserAssignedIdentities}${resourceToken}'
    location: location
    tags: tags
  }
}

// Azure Speech Services (S0 tier as specified in TDD)
module speechServices './core/ai/speech-services.bicep' = {
  name: 'speech-services'
  scope: rg
  params: {
    name: '${abbrs.cognitiveServicesAccounts}speech-${resourceToken}'
    location: location
    tags: tags
    sku: 'S0'
    managedIdentityPrincipalId: managedIdentity.outputs.principalId
  }
}

// Azure Storage Account for avatar videos and temp files
module storageAccount './core/storage/storage-account.bicep' = {
  name: 'storage-account'
  scope: rg
  params: {
    name: '${abbrs.storageStorageAccounts}${resourceToken}'
    location: location
    tags: tags
    containers: ['avatars', 'audio']
  }
}

// Azure Key Vault for secure credential storage
module keyVault './core/security/keyvault.bicep' = {
  name: 'key-vault'
  scope: rg
  params: {
    name: '${abbrs.keyVaultVaults}${resourceToken}'
    location: location
    tags: tags
    principalId: managedIdentity.outputs.principalId
  }
}

// Log Analytics Workspace
module logAnalyticsWorkspace './core/monitor/loganalytics.bicep' = {
  name: 'log-analytics'
  scope: rg
  params: {
    name: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    location: location
    tags: tags
  }
}

// Application Insights for monitoring
module applicationInsights './core/monitor/applicationinsights.bicep' = {
  name: 'application-insights'
  scope: rg
  params: {
    name: '${abbrs.insightsComponents}${resourceToken}'
    location: location
    tags: tags
    workspaceResourceId: logAnalyticsWorkspace.outputs.id
  }
}

// Container Registry for Docker images
module containerRegistry './core/host/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    tags: tags
    principalId: managedIdentity.outputs.principalId
  }
}

// Container Apps Environment with Log Analytics integration
module containerAppsEnvironment './core/host/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    tags: tags
    logAnalyticsWorkspaceResourceId: logAnalyticsWorkspace.outputs.id
    applicationInsightsConnectionString: applicationInsights.outputs.connectionString
  }
}

// Container App for Flask application
module webApp './core/host/container-app.bicep' = {
  name: 'web-app'
  scope: rg
  params: {
    name: '${abbrs.appContainerApps}web-${resourceToken}'
    location: location
    tags: union(tags, { 'azd-service-name': 'web' })
    containerAppsEnvironmentId: containerAppsEnvironment.outputs.id
    containerRegistryLoginServer: containerRegistry.outputs.loginServer
    userAssignedIdentityId: managedIdentity.outputs.id
    containerImage: !empty(containerImage) ? containerImage : 'nginx:alpine'
    minReplicas: 1
    maxReplicas: 3
    environmentVariables: [
      {
        name: 'AZURE_SPEECH_KEY'
        secretRef: 'azure-speech-key'
      }
      {
        name: 'AZURE_SPEECH_REGION'
        value: location
      }
      {
        name: 'AZURE_OPENAI_ENDPOINT'
        value: azureOpenAIEndpoint
      }
      {
        name: 'AZURE_OPENAI_KEY'
        secretRef: 'azure-openai-key'
      }
      {
        name: 'AZURE_STORAGE_CONNECTION_STRING'
        secretRef: 'azure-storage-connection-string'
      }
      {
        name: 'FLASK_SECRET_KEY'
        secretRef: 'flask-secret-key'
      }
      {
        name: 'FLASK_ENV'
        value: 'production'
      }
      {
        name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
        value: applicationInsights.outputs.connectionString
      }
    ]
    secrets: [
      {
        name: 'azure-speech-key'
        keyVaultUrl: '${keyVault.outputs.vaultUri}secrets/azure-speech-key'
        identity: managedIdentity.outputs.id
      }
      {
        name: 'azure-openai-key'
        keyVaultUrl: '${keyVault.outputs.vaultUri}secrets/azure-openai-key'
        identity: managedIdentity.outputs.id
      }
      {
        name: 'azure-storage-connection-string'
        keyVaultUrl: '${keyVault.outputs.vaultUri}secrets/azure-storage-connection-string'
        identity: managedIdentity.outputs.id
      }
      {
        name: 'flask-secret-key'
        keyVaultUrl: '${keyVault.outputs.vaultUri}secrets/flask-secret-key'
        identity: managedIdentity.outputs.id
      }
    ]
  }
  dependsOn: [
    keyVaultSecrets
  ]
}

// Store secrets in Key Vault
module keyVaultSecrets './core/security/keyvault-secrets.bicep' = {
  name: 'key-vault-secrets'
  scope: rg
  params: {
    keyVaultName: keyVault.outputs.name
    secrets: [
      {
        name: 'azure-speech-key'
        value: speechServices.outputs.key
      }
      {
        name: 'azure-openai-key'
        value: azureOpenAIKey
      }
      {
        name: 'azure-storage-connection-string'
        value: storageAccount.outputs.connectionString
      }
      {
        name: 'flask-secret-key'
        value: base64(uniqueString(subscription().subscriptionId, environmentName))
      }
    ]
  }
}

// Output values as specified in TDD
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name

output AZURE_SPEECH_ENDPOINT string = speechServices.outputs.endpoint
output AZURE_SPEECH_KEY string = speechServices.outputs.key
output AZURE_SPEECH_REGION string = location

output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.outputs.name
output AZURE_STORAGE_CONNECTION_STRING string = storageAccount.outputs.connectionString

output AZURE_KEY_VAULT_NAME string = keyVault.outputs.name
output AZURE_KEY_VAULT_ENDPOINT string = keyVault.outputs.vaultUri

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name

output WEB_APP_NAME string = webApp.outputs.name
output WEB_APP_URI string = webApp.outputs.uri
output WEB_APP_FQDN string = webApp.outputs.fqdn

output AZURE_CONTAINER_APPS_ENVIRONMENT_NAME string = containerAppsEnvironment.outputs.name

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = managedIdentity.outputs.principalId
output SERVICE_WEB_NAME string = webApp.outputs.name
output SERVICE_WEB_URI string = webApp.outputs.uri
output SERVICE_WEB_FQDN string = webApp.outputs.fqdn
