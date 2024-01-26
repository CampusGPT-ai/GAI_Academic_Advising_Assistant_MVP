# Deployment steps

## will refine this documentation as the process stabilizes

### pre-flight set up

1. Ensure subscription is registered for the following resource providers: 
- Microsoft.CognitiveServices
- Microsoft.Search
- Microsoft.DocumentDB
- Microsoft.ContainerRegistry
- Microsoft.ContainerInstance

2. create service principal, managed identity, and resource groups in azure portal or CLI.  Note rg name, managed identity name, client id, tenant id, and secret
3. run bicep template in what_if_deployments, look for errors and correct
4. configure environment variables in azure application, respecting specific required naming
4. configure application authorization - enable microsoft auth with service principal

### app/server build and test
3. run setup_env_[linux or windows].ps1/sh to propogate environment variables for local testing
5. run curl commands in postman or cmd, check api results
6. build docker container (build.ps1)


### client build and test
1. ensure that node -v > 16 and npm -v > 8 are install locally
2. navigate to client directory and run npm install in terminal
3. npm run build to create a local project build
3. *optional  - npm run build-storybook to create storybook build
3. npm run storybook to view/test individual components
4. npm start to preview app in localhost
5. update base url in client>src>api>baseURL to webpp url from azure app service for dev and prod


## troubleshoot
### Port configuration
you can change the port that the react app runs on for local testing by setting react app port in the .env REACT_APP_PORT=3000


