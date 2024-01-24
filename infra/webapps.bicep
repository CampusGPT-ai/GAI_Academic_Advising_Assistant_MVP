param location string = resourceGroup().location // Location for all resources

var resourceTags = {
  application: 'tl chen campusevolve ai advisor'
  department: 'cos physics'
  environment: 'poc'
  expenseid: 'ucfel0002333'
}
param appName string = uniqueString(resourceGroup().id)
//container registry params
var containerRegistryName = toLower('acr${appName}')

param containerRegistryAdminEnabled bool = true

//Docker images
//DOCKER|<image-name>:<tag>
var pythonDockerImage = toLower('pdi${appName}:latest') // Replace with your Python Docker image
var nodeDockerImage = toLower('ndi${appName}:latest') // Replace with your Node Docker image
var pythonlinuxFxVersion = 'DOCKER|${pythonDockerImage}'
var nodelinuxFxVersion = 'DOCKER|${nodeDockerImage}'

//web app params
var pythonWebAppName = toLower('python${appName}')
var nodeWebAppName = toLower('node${appName}')
var appServicePlanName = toLower('AppServicePlan${appName}')

// SKUs
param appServiceSKU string = 'S1'
param containerRegistrySKU string = 'Basic'

// environment variables
var storageAccountName = 'blob${appName}'
var storageContainerName = 'index-processed'

@secure()
param storageAccountKey string
param openAIDeploymentName string
param embeddingModel string
param openAIModelName string 
param openAIVersion string

//container registry
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2019-05-01' = {
  name: containerRegistryName
  location: location
  sku: {
    name: containerRegistrySKU
  }
  properties: {
    adminUserEnabled: containerRegistryAdminEnabled
  }
  tags: resourceTags
}

// app services
resource appServicePlan 'Microsoft.Web/serverfarms@2020-06-01' = {
  name: appServicePlanName
  location: location
  properties: {
    reserved: true
  }
  sku: {
    name: appServiceSKU
  }
  kind: 'linux'
  tags: resourceTags
}

resource pythonAppService 'Microsoft.Web/sites@2020-06-01' = {
  name: pythonWebAppName
  location: location
  tags: resourceTags
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: pythonlinuxFxVersion
        appSettings: [
          {
            name: 'AZURE_STORAGE_ACCOUNT'
            value: storageAccountName
          }
          {
            name: 'AZURE_STORAGE_CONTAINER'
            value: storageContainerName
          }
          {
            name: 'AZURE_STORAGE_ACCOUNT_CRED'
            value: storageAccountKey
          }
          {
            name: 'DEPLOYMENT_NAME'
            value: openAIDeploymentName
          }
          {
            name: 'DOCKER_REGISTRY_SERVER_PASSWORD'
            value: 'none'
          }
          {
            name: 'DOCKER_REGISTRY_SERVER_URL'
            value: 'https://acr${appName}.azurecr.io'
          }
          {
            name: 'DOCKER_REGISTRY_SERVER_USERNAME'
            value: 'none'
          }
          {
            name: 'EMBEDDING'
            value: embeddingModel
          }
          {
            name: 'HISTORY_WINDOW_SIZE'
            value: '10'
          }
          {
            name: 'KB_FIELDS_CONTENT'
            value: 'content_vector'
          }
          {
            name: 'KB_FIELDS_SOURCEPAGE'
            value: 'source'
          }
          {
            name: 'MODEL_NAME'
            value: openAIModelName
          }
          {
            name: 'MONGO_CONN_STR'
            value: 'none'
          }
          {
            name: 'MONGO_DB'
            value: 'cosmos${appName}'
          }
          {
            name: 'OPENAI_API_BASE'
            value: 'https://eastus.api.cognitive.microsoft.com/'
          }
          {
            name: 'OPENAI_API_KEY'
            value: 'none'
          }
          {
            name: 'OPENAI_API_TYPE'
            value: 'azure'
          }
          {
            name: 'OPENAI_API_VERSION'
            value: openAIVersion
          }
          {
            name: 'RAW_MESSAGE_COLLECTION'
            value: 'raw_message_history'
          }
          {
            name: 'SEARCH_API_KEY'
            value: 'none'
          }
          {
            name: 'SEARCH_ENDPOINT'
            value: 'https://search${appName}.search.windows.net'
          }
          {
            name: 'SEARCH_INDEX_NAME'
            value: 'none'
          }
        ]
    }
  }
}

// deployment slots
resource pythonDevSlot 'Microsoft.Web/sites/slots@2021-02-01' = {
  name: 'development'
  tags: resourceTags
  parent: pythonAppService
  location: location
  kind: 'app'
  properties: {
    serverFarmId: appServicePlan.id
  }
}

resource nodeAppService 'Microsoft.Web/sites@2020-06-01' = {
  name: nodeWebAppName
  location: location
  tags: resourceTags
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: nodelinuxFxVersion
      appSettings: [
        {
          name: 'REACT_APP_DOMAIN'
          value: 'production'
        }
        {
          name: 'REACT_APP_WEBENV'
          value: 'development'
        }
      ]
    }
  }
}

// deployment slots
resource nodeDevSlot 'Microsoft.Web/sites/slots@2021-02-01' = {
  name: 'development'
  tags: resourceTags
  parent: nodeAppService
  location: location
  kind: 'app'
  properties: {
    serverFarmId: appServicePlan.id
  }
}

