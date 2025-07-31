@description('Application Insights name')
param name string

@description('Location for Application Insights')
param location string = resourceGroup().location

@description('Tags to apply to Application Insights')
param tags object = {}

@description('Log Analytics Workspace ID')
param workspaceResourceId string

@description('Application type')
param kind string = 'web'

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  tags: tags
  kind: kind
  properties: {
    Application_Type: kind
    WorkspaceResourceId: workspaceResourceId
    IngestionMode: 'LogAnalytics'
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }
}

@description('Application Insights name')
output name string = applicationInsights.name

@description('Application Insights ID')
output id string = applicationInsights.id

@description('Application Insights instrumentation key')
output instrumentationKey string = applicationInsights.properties.InstrumentationKey

@description('Application Insights connection string')
output connectionString string = applicationInsights.properties.ConnectionString
