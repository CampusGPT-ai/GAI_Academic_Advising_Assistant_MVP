# Define variables
rg='ce-advisor-poc'
location='eastus'
identity_name="ce-advisor-admin"

# Define tags
tags="application='tl chen campusevolve ai advisor' department='cos physics' environment='poc' expenseid='ucfel0002333'"

# Log in to Azure (this will prompt a login via the browser)
az login

rg_id="gnoba4quzzn5u"


# az deployment group what-if --resource-group $rg --template-file 'containers.bicep' --parameters @params_containers.json
az deployment group what-if --resource-group $rg --template-file 'webapps.bicep' --parameters @params_webapp.json