#!/bin/bash
az login

# Define the Azure Web App name and resource group
WEB_APP_NAME="pythongnoba4quzzn5u"
RESOURCE_GROUP="ce-advisor-poc"

# Log in to Azure (Uncomment this line if you're not already logged in)
# az login

# Get the app settings (environment variables) in JSON format
env_vars=$(az webapp config appsettings list --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP)

# Check if the command was successful
if [ $? -ne 0 ]; then
    echo "Failed to retrieve environment variables."
    exit 1
fi

# Iterate over the environment variables and export them
echo "Setting environment variables..."
for row in $(echo "${env_vars}" | jq -r '.[] | @base64'); do
    _jq() {
     echo ${row} | base64 --decode | jq -r ${1}
    }

    key=$(_jq '.name')
    value=$(_jq '.value')
    
    # Export the variable to the OS environment
    export "$key=$value"
done

# Output to a .env file
echo "Writing to .env file..."
for row in $(echo "${env_vars}" | jq -r '.[] | @base64'); do
    _jq() {
     echo ${row} | base64 --decode | jq -r ${1}
    }

    key=$(_jq '.name')
    value=$(_jq '.value')

    # Write the variable to .env file
    echo "$key=$value" >> .env
done
