targetScope = 'subscription'

@minLength(1)
@maxLength(64)
@description('Name of the the environment which is used to generate a short unique hash used in all resources.')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Location for OpenAI resource')
@allowed(['canadaeast', 'eastus', 'eastus2', 'francecentral', 'japaneast', 'northcentralus', 'swedencentral', 'switzerlandnorth', 'uksouth', 'westeurope', 'westus'])
@metadata({
  azd: {
    type: 'location'
  }
})
param openAiLocation string = 'eastus'

// Optional parameters to override the default azd resource naming conventions. Update the main.parameters.json file to set the values.
var abbrs = loadJsonContent('./abbreviations.json')
var resourceToken = toLower(uniqueString(subscription().id, environmentName, location))
var tags = { 'azd-env-name': environmentName }

// Organize resources in a resource group
resource rg 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: '${abbrs.resourcesResourceGroups}${environmentName}'
  location: location
  tags: tags
}

// Create Azure Speech Services
module speechServices './core/ai/speech-services.bicep' = {
  name: 'speech-services'
  scope: rg
  params: {
    name: '${abbrs.cognitiveServicesAccounts}speech-${resourceToken}'
    location: location
    tags: tags
    sku: 'S0'
    customSubDomainName: '${abbrs.cognitiveServicesAccounts}speech-${resourceToken}'
  }
}

// Create Container Apps Environment
module containerAppsEnvironment './core/host/container-apps-environment.bicep' = {
  name: 'container-apps-environment'
  scope: rg
  params: {
    name: '${abbrs.appManagedEnvironments}${resourceToken}'
    location: location
    tags: tags
  }
}

// Create the web frontend
module web './core/host/container-app.bicep' = {
  name: 'web'
  scope: rg
  params: {
    name: '${abbrs.appContainerApps}web-${resourceToken}'
    location: location
    tags: tags
    containerAppsEnvironmentName: containerAppsEnvironment.outputs.name
    containerRegistryName: containerRegistry.outputs.name
    env: [
      {
        name: 'AZURE_SPEECH_KEY'
        value: speechServices.outputs.key
      }
      {
        name: 'AZURE_SPEECH_REGION'
        value: location
      }
      {
        name: 'FLASK_ENV'
        value: 'production'
      }
    ]
    external: true
    targetPort: 5000
  }
}

// Create Azure Container Registry
module containerRegistry './core/host/container-registry.bicep' = {
  name: 'container-registry'
  scope: rg
  params: {
    name: '${abbrs.containerRegistryRegistries}${resourceToken}'
    location: location
    tags: tags
  }
}

// Create Log Analytics Workspace
module logAnalyticsWorkspace './core/monitor/loganalytics.bicep' = {
  name: 'log-analytics'
  scope: rg
  params: {
    name: '${abbrs.operationalInsightsWorkspaces}${resourceToken}'
    location: location
    tags: tags
  }
}

// Output the service endpoints
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP string = rg.name

output AZURE_SPEECH_ENDPOINT string = speechServices.outputs.endpoint
output AZURE_SPEECH_KEY string = speechServices.outputs.key
output AZURE_SPEECH_REGION string = location

output AZURE_CONTAINER_REGISTRY_ENDPOINT string = containerRegistry.outputs.loginServer
output AZURE_CONTAINER_REGISTRY_NAME string = containerRegistry.outputs.name

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = web.outputs.identityPrincipalId
output SERVICE_WEB_NAME string = web.outputs.name
output SERVICE_WEB_URI string = web.outputs.uri
