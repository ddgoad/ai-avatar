metadata description = 'Creates a Log Analytics workspace.'

@description('Name of the Log Analytics workspace.')
param name string

@description('Location for the Log Analytics workspace.')
param location string = resourceGroup().location

@description('Tags to apply to the Log Analytics workspace.')
param tags object = {}

resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: name
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 90
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Output values
output id string = logAnalyticsWorkspace.id
output name string = logAnalyticsWorkspace.name
output customerId string = logAnalyticsWorkspace.properties.customerId