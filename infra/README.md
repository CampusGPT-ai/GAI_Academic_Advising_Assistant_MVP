# Deployment steps

## will refine this documentation as the process stabilizes


2. create service principal and resource groups in azure portal or CLI.  Note rg name, client id, tenant id, and secret
1. run bicep template in what_if_deployments, look for errors and correct
2. configure environment variables in azure application, respecting specific required naming
4. configure application authorization - enable microsoft auth with service principal
3. run setup_env_[linux or windows].ps1/sh to propogate environment variables for local testing
5. run curl commands in postman or cmd, check api results
6. build docker container (build.ps1)
7. client stuff...coming
