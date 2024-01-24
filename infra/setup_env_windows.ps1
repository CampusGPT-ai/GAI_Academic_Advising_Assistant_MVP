# PowerShell script to install jq, get Azure Web App environment variables, and write them to a .env file

# Define the Azure Web App name and resource group
$WEB_APP_NAME="pythongnoba4quzzn5u"
$RESOURCE_GROUP="ce-advisor-poc"
# Function to check if jq is installed
function Check-InstallJq {
    if (-not (Get-Command "jq" -ErrorAction SilentlyContinue)) {
        Write-Host "jq not found. Installing..."
        $jqUrl = "https://github.com/stedolan/jq/releases/download/jq-1.6/jq-win64.exe"
        Invoke-WebRequest -Uri $jqUrl -OutFile "jq.exe"
        Move-Item "jq.exe" -Destination "C:\Windows\System32\jq.exe"
    } else {
        Write-Host "jq is already installed."
    }
}

# Check and install jq
Check-InstallJq

# Log in to Azure (uncomment the next line if not already logged in)
# Login-AzAccount

# Get environment variables from Azure Web App
$envVars = az webapp config appsettings list --name $WEB_APP_NAME --resource-group $RESOURCE_GROUP | ConvertFrom-Json

# Check if the command was successful
if ($null -eq $envVars) {
    Write-Host "Failed to retrieve environment variables."
    exit
}

# Create or clear .env file
$envFilePath = ".\.env"
if (Test-Path $envFilePath) {
    Clear-Content $envFilePath
} else {
    New-Item -Path $envFilePath -ItemType File
}

# Iterate over the environment variables and add them to the .env file
foreach ($var in $envVars) {
    "$($var.name)=$($var.value)" | Out-File -FilePath $envFilePath -Append
}

Write-Host "Environment variables are set and .env file is created at $envFilePath."
