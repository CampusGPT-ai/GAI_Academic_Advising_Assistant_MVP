# .\setupenv.ps1 -WEBAPP_NAME "ce-demo-app/dev" etc

param(
    [Parameter(Mandatory=$true)]
    [string]$WEBAPP_NAME,

    [Parameter(Mandatory=$true)]
    [string]$SLOT_NAME
)

az login


# Resource Group of your Azure Web App
$RESOURCE_GROUP = "demo-deployment"

# Read the .env file line by line
Get-Content .env | ForEach-Object {
    # Split each line into key and value based on the '=' delimiter
    $keyValue = $_ -split "=", 2

    # Ensure the line contains a key and a value
    if ($keyValue.Count -eq 2) {
        $key = $keyValue[0]
        $value = $keyValue[1]

        # Use az CLI to set the app setting for Azure Web App
        az webapp config appsettings set --resource-group $RESOURCE_GROUP --name $WEBAPP_NAME --slot $SLOT_NAME --settings "$key=$value"
    }
}
