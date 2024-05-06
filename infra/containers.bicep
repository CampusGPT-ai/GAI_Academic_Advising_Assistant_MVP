param location string = resourceGroup().location // Location for all resources
param rgName string = resourceGroup().name

param managedIdentity string

var resourceTags = {
  application: 'campusevolve ai advisor'
  //department: 'cos physics'
  environment: 'poc'
  //expenseid: 'ucfel0002333'
}
var appName= uniqueString(resourceGroup().id)

//storage params
var dbName = toLower('cosmos${appName}')
var searchServiceName = toLower('search${appName}')
var blobStorageName = toLower('blob${appName}')
var cognitiveServiceName = toLower('openai${appName}')

// SKUs
param openAISKU string = 'S0'
param searchSKU string = 'basic'
param blogSKU string = 'Standard_LRS'


// cosmos db - only account and db are created here, app creates collections
resource cosmosDbAccount 'Microsoft.DocumentDB/databaseAccounts@2021-06-15' = {
  name: dbName
  tags: resourceTags
  location: location
  kind: 'MongoDB'
  properties: {
    databaseAccountOfferType: 'Standard'
    locations: [
      {
        locationName: location
        failoverPriority: 0
      }
    ]
  }
}

resource database 'Microsoft.DocumentDB/databaseAccounts/mongodbDatabases@2022-05-15' = {
  parent: cosmosDbAccount
  name: dbName
  tags: resourceTags
  properties: {
    resource: {
      id: dbName
    }
    options: {
      autoscaleSettings: {
        maxThroughput: 1000
      }
    }
  }
}


// search services - currently can't create the index, use the json definition in the scraper module 
resource search 'Microsoft.Search/searchServices@2020-08-01' = {
  name: searchServiceName
  tags: resourceTags
  location: location
  sku: {
    name: searchSKU
  }
  properties: {
    replicaCount: 1
    partitionCount: 1
    hostingMode: 'default'
  }
}

// open ai deployments
// resource cognitiveService 'Microsoft.CognitiveServices/accounts@2021-10-01' = {
//  name: cognitiveServiceName
//   tags: resourceTags
//   location: location
//   sku: {
//     name: openAISKU
//   }
//   kind: 'OpenAI'
//   properties: {
//     restore: false
//     apiProperties: {
//       statisticsEnabled: false
//     }
//   }
// }

// blob storage
resource blobStorage 'Microsoft.Storage/storageAccounts@2021-04-01' = {
  name: blobStorageName
  properties: {
    supportsHttpsTrafficOnly: true
  }
  tags: resourceTags
  location: location
  kind: 'StorageV2'
  sku: {
    name: blogSKU
  }
}

// Define the Blob Service (required for defining containers)
resource blobService 'Microsoft.Storage/storageAccounts/blobServices@2021-04-01' = {
  name: 'default'
  parent: blobStorage
  // Other properties if needed
}

// Define the Blob Container
resource logsBlobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-04-01' = {
  name: 'logs'
  parent: blobService
  // Other properties if needed, like public access level
}


// Define the Blob Container
resource indexBlobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-04-01' = {
  name: 'index-upload'
  parent: blobService
  // Other properties if needed, like public access level
}

// Define the Blob Container
resource processedBlobContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-04-01' = {
  name: 'index-processed'
  parent: blobService
  // Other properties if needed, like public access level
}
