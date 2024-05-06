$ErrorActionPreference = "Stop"
$AppImage = "app-backend-dev"
$ClientImage = "client-frontend-dev"
# Docker registry
$Registry = "acrgnoba4quzzn5u"
$tag = "latest"
#az acr build --registry acrgnoba4quzzn5u --image client-frontend-dev --tag latest .

function PromptForPush($containerPath, $defaultImageName) {
    $pushDecision = $false
    $imageName = $defaultImageName
    
    $pathinput = Read-Host "Do you want to npush the image for $containerPath? (y/n)"
    if ($pathinput -eq "y") {
        az login
        az acr login -n $Registry
        az acr update -n $Registry --admin-enabled true
        $pushDecision = $true
        $imageName = Read-Host "Enter the image name for $containerPath (default: $defaultImageName)"
        if (-not $imageName) {
            $imageName = $defaultImageName
        }
    }

    return @{
        ShouldPush = $pushDecision
        ImageName  = $imageName
    }
}

function StopContainerOnPort($port) {
    $container = docker ps --format '{{.ID}} {{.Ports}}' | Where-Object { $_ -like "*:$port->$port/tcp*" } | ForEach-Object { $_ -split " " | Select-Object -First 1 }
    if ($container) {
        docker stop $container
    }
}

# Stop containers on ports 8000 and 5000
StopContainerOnPort 8000
StopContainerOnPort 5000

function BuildAndRunContainer($path, $imageName, $port, $push) {
    Push-Location -Path $path
    
    $FullImageName = "{0}:{1}" -f $imageName, $tag


       # Build the Docker image
    $buildArgs = Get-Content .env | Where-Object { $_ -match "^[a-zA-Z_]+[a-zA-Z0-9_]*=.*$" } | ForEach-Object {
    $keyValue = $_ -split "=", 2
    "--build-arg", "$($keyValue[0])=$($keyValue[1])"
    }
    docker build --no-cache --platform=linux/amd64 $buildArgs -t $imageName .
    docker tag $imageName $FullImageName
    if ($push) {
        docker push $FullImageName
    }
 
    
    # Initialize empty environment variable array
    $envVars = @()

    $envVars = Get-Content .env | Where-Object { $_ -match "^[a-zA-Z_]+[a-zA-Z0-9_]*=.*$" } | ForEach-Object {
        $keyValue = $_ -split "=", 2
        "--env", "$($keyValue[0])=$($keyValue[1])"    
    }

    # Display values before running the command
        Write-Host "Running docker with the following details:"
        Write-Host "Port: $port"
        Write-Host "Environment Variables: $envVars"
        Write-Host "Full Image Name: $FullImageName"

    # Run the image on the specified port

    docker run --rm -d -p ${port}:${port} --platform linux/amd64 --env-file ./.env -v ${PWD}/.env:/.env  $FullImageName
    Pop-Location
}

$response = PromptForPush "./app" $AppImage
BuildAndRunContainer "./app" $response.ImageName 8000 $response.ShouldPush

$response = PromptForPush "./client/" $ClientImage
BuildAndRunContainer "./client" $response.ImageName 5000 $response.ShouldPush
