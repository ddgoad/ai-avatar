@description('Container app name')
param name string

@description('Location for the container app')
param location string = resourceGroup().location

@description('Tags to apply to the container app')
param tags object = {}

@description('Container Apps Environment ID')
param containerAppsEnvironmentId string

@description('Container registry login server')
param containerRegistryLoginServer string

@description('User assigned identity ID')
param userAssignedIdentityId string

@description('Container image')
param containerImage string

@description('Target port for the container')
param targetPort int = 5000

@description('Environment variables')
param environmentVariables array = []

@description('Secrets')
param secrets array = []

@description('CPU and memory configuration')
param resources object = {
  cpu: json('0.5')
  memory: '1Gi'
}

@description('Minimum replica count')
param minReplicas int = 0

@description('Maximum replica count')
param maxReplicas int = 3

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: name
  location: location
  tags: tags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentityId}': {}
    }
  }
  properties: {
    environmentId: containerAppsEnvironmentId
    configuration: {
      ingress: {
        external: true
        targetPort: targetPort
        transport: 'http'
        corsPolicy: {
          allowedOrigins: ['*']
          allowedMethods: ['*']
          allowedHeaders: ['*']
          allowCredentials: true
        }
      }
      registries: [
        {
          server: containerRegistryLoginServer
          identity: userAssignedIdentityId
        }
      ]
      secrets: [for secret in secrets: {
        name: secret.name
        keyVaultUrl: secret.keyVaultUrl
        identity: secret.identity
      }]
    }
    template: {
      containers: [
        {
          name: name
          image: containerImage
          resources: resources
          env: environmentVariables
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: targetPort
                scheme: 'HTTP'
              }
              initialDelaySeconds: 60
              periodSeconds: 30
              timeoutSeconds: 10
              successThreshold: 1
              failureThreshold: 5
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: targetPort
                scheme: 'HTTP'
              }
              initialDelaySeconds: 45
              periodSeconds: 10
              timeoutSeconds: 5
              successThreshold: 1
              failureThreshold: 5
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-requests'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }
    }
  }
}

@description('Container app name')
output name string = containerApp.name

@description('Container app ID')
output id string = containerApp.id

@description('Container app FQDN')
output fqdn string = containerApp.properties.configuration.ingress.fqdn

@description('Container app URL')
output uri string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
