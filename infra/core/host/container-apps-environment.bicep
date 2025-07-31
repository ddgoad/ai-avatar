metadata description = 'Creates a Container Apps Environment for hosting container apps.'

@description('Name of the Container Apps Environment.')
param name string

@description('Location for the Container Apps Environment.')
param location string = resourceGroup().location

@description('Tags to apply to the Container Apps Environment.')
param tags object = {}

@description('Resource ID of the Log Analytics workspace.')
param logAnalyticsWorkspaceResourceId string

@description('Application Insights connection string.')
param applicationInsightsConnectionString string = ''

resource containerAppsEnvironment 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspace.properties.customerId
        sharedKey: logAnalyticsWorkspace.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
  }
}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' existing = {
  name: last(split(logAnalyticsWorkspaceResourceId, '/'))
}

// Output values
output id string = containerAppsEnvironment.id
output name string = containerAppsEnvironment.name
output defaultDomain string = containerAppsEnvironment.properties.defaultDomain