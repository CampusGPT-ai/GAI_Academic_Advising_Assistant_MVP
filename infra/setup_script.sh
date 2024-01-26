rg='ce-advisor-poc'
location='eastus'
identity_name="ce-advisor-admin"

# Define tags
tags="application='tl chen campusevolve ai advisor' department='cos physics' environment='poc' expenseid='ucfel0002333'"

# Log in to Azure (this will prompt a login via the browser)
az login

rg_id=$(az group show --name $rg --query id -o tsv)
saname="cosmos${rg_id}"

# run bicep to set up storage
#az deployment group create --resource-group $rg --template-file 'containers.bicep'

# get keys

sakey=az storage account keys list --account-name $saname --resource-group $rg --query '[0].value' -o tsv
echo $sakey

# run bicep 
az deployment group create --resource-group $rg --template-file 'webapps.bicep' --parameters storageAccountKey=$sakey
