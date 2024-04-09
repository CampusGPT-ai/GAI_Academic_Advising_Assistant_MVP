#!/bin/bash
set -e

AppImage="app"
ClientImage="client"
# Docker registry
Registry="acrgnoba4quzzn5u"
tag="latest"
# az acr build --registry acrgnoba4quzzn5u --image client-frontend-dev --tag latest .

prompt_for_push() {
    pushDecision=false
    imageName=$1 # Default image name passed as an argument

    read -p "Do you want to push the image for $2? (y/n): " pathinput
    if [ "$pathinput" == "y" ]; then
        az login
        az acr login -n $Registry
        az acr update -n $Registry --admin-enabled true
        pushDecision=true
        read -p "Enter the image name for $2 (default: $1): " imageNameInput
        if [ -n "${imageNameInput}" ]; then
            imageName=${imageNameInput}
        else
            imageName=$1
        fi

    fi

    echo "$pushDecision $imageName"
}

stop_container_on_port() {
    container=$(docker ps --format '{{.ID}} {{.Ports}}' | grep ":$1->" | awk '{print $1}')
    if [ -n "${container}" ]; then
        docker stop $container
    fi
}

# Stop containers on ports 8000 and 5000
stop_container_on_port 8000
stop_container_on_port 5000

build_and_run_container() {
    pushd $1 > /dev/null
    echo "Image name parameter: $2"
    echo "Tag: ${tag}"

    FullImageName="${2}:${tag}"

    # Build the Docker image
    buildArgs=$(awk -F= '$1 ~ /^[a-zA-Z_]+[a-zA-Z0-9_]*$/ {print "--build-arg " $1 "=" $2}' .env)
    echo docker buildx build --no-cache --platform=linux/amd64 $buildArgs -t $2 .

    docker buildx build --platform=linux/amd64 $buildArgs -t $2 .
    docker tag $2 $FullImageName
    if [ "$4" == "true" ]; then
        docker push $FullImageName
    fi

    # Initialize environment variables from .env file for docker run
    envVars=$(awk -F= '$1 ~ /^[a-zA-Z_]+[a-zA-Z0-9_]*$/ {print "-e " $1 "=" $2}' .env | xargs)

    # Display values before running the command
    echo "Running docker with the following details:"
    echo "Port: $3"
    echo "Environment Variables: $envVars"
    echo "Full Image Name: $FullImageName"

    # Run the image on the specified port
    docker run --rm -d -p ${3}:${3} --platform linux/amd64 --env-file ./.env $FullImageName

    popd > /dev/null
}

# Main
response=$(prompt_for_push "$AppImage" "./app")
read pushDecision imageName <<< $response
build_and_run_container "./app" $imageName 8000 $pushDecision

response=$(prompt_for_push "$ClientImage" "./client/")
read pushDecision imageName <<< $response
build_and_run_container "./client" $imageName 3000 $pushDecision
