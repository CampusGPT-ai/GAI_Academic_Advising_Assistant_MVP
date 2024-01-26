# Define variables
rg='AI-Advisor'
location='eastus'
identity_name="ce-advisor-admin"

# Define tags
tags="application='campusevolve ai advisor' environment='poc'"

# Log in to Azure (this will prompt a login via the browser)
az login

rg_id="gnoba4quzzn5u"


az deployment group create --resource-group $rg --template-file 'containers.bicep' --parameters @params_container.json


# az deployment group what-if --resource-group $rg --template-file 'containers.bicep' --parameters @params_container.json
# az deployment group what-if  --resource-group $rg --template-file 'webapps.bicep' --parameters @params_webapp.json