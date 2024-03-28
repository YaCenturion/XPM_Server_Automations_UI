#!/bin/bash
# sudo chmod a+x automation.sh

# example: bash automation.sh . expim-ops 73 master
# '.' :: current folder
# 'expim-ops' :: name for container
# '73' :: just number tag version for docker when running container
# 'master' :: tag_prefix
# Result like: expim-ops:master-v73


################## DOCKER CHECK-UP ######################
if ! command -v docker &>/dev/null; then
    echo ">>> >>> --- ERROR: Docker not found"
    exit 1
fi

################## GET VARS ######################
app_folder="${1:-/srv/SandBox}"
docker_name="${2:-expim_NotSetName}"
tag_version="${3:-_no_revision}"
tag_prefix="${4:-_no_tag_prefix}"
docker_port=80
[[ ! $tag_prefix =~ ^(master|prod|main)$ ]] && docker_port=8080 && echo ">>> >>> >>> INFO: Docker use special port: $docker_port"


# Set folder to the current working directory if the first argument is "."
if [ "$app_folder" == "." ]; then
  app_folder=$(pwd)
fi
db_folder=$(dirname "$app_folder")/db
# Add DB folder if not exist
mkdir -p "$db_folder"


# Check Docker container name
if [ "$docker_name" == "expim_NotSetName" ]; then
  echo ">>> >>> --- WARNING! Not set Docker container name. Using: $docker_name"
fi


################## BUIDL & RUN DOCKER ######################
# Docker stop & clear
docker ps -a
docker stop "$docker_name"
docker rm "$docker_name"
docker container prune -f


echo -e ">>> >>> >>> INFO: Build container $docker_name:$tag_prefix-v$tag_version"
docker build -t "$docker_name":"$tag_prefix"-v"$tag_version" .


# Checking docknet
NETWORK_NAME="docknet"
if ! docker network inspect "$NETWORK_NAME" &>/dev/null; then
    # Create docker network
    if ! docker network create --subnet=172.29.3.0/16 $NETWORK_NAME; then
        echo ">>> >>> --- ERROR: When try create network: $NETWORK_NAME."
        exit 1
    fi
fi


echo -e ">>> >>> >>> INFO: Run container $docker_name:$tag_prefix-v$tag_version"
docker run -d -e APP_BUILD_VERSION="$tag_version" -v "$db_folder"/instance:/app/instance -p "$docker_port":5000 --network=docknet --name "$docker_name" --restart=unless-stopped "$docker_name":"$tag_prefix"-v"$tag_version" || {
    echo ">>> >>> --- ERROR: When running Docker container."
    exit 1
}
