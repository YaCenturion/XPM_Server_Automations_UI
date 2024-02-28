#!/bin/bash
# sudo chmod a+x automation.sh

# example: bash automation.sh . expim-ops 73
# . - current folder
# expim-ops - name for container
# 73 - just number tag version for docker when running container


################## GET VARS ######################
#if [[ $# -eq 3 ]]; then
folder="${1:-'/srv/SandBox'}"
docker_name="${2:-'expim_NotSetName'}"
tag_version="${3:-'_no_revision'}"

if [ "$folder" == "." ]; then
  # Set folder to the current working directory if the first argument is "."
  folder=$(pwd)
fi
if [ "$docker_name" == "expim_NotSetName" ]; then
  echo -e "############ WARNING! ############"
  echo -e "FOLDER: $folder and TAG: $tag_version"
  echo -e "############# ###### #############"
fi


echo -e "############ Docker stop & clear ############"
docker ps -a
docker stop "$docker_name"
docker rm "$docker_name"
docker container prune -f


echo -e "############ Build container $docker_name:prod-v$tag_version ############"
docker build -t "$docker_name":prod-v"$tag_version" .


echo -e "############ Checking docknet ############"
NETWORK_NAME="docknet"
if docker network inspect $NETWORK_NAME &>/dev/null; then
  echo "Network '$NETWORK_NAME' already exist."
else
    # Create docker network
    if docker network create --subnet=172.29.3.0/16 $NETWORK_NAME; then
        echo "Network '$NETWORK_NAME' created."
    else
        echo "Error when try create network: '$NETWORK_NAME'."
        exit 1
    fi
fi


echo -e "############ Run container $docker_name:prod-v$tag_version ############"
docker run -d -e APP_BUILD_VERSION="$tag_version" -v "$folder"/instance:/app/instance -p 80:5000 --network=docknet --name "$docker_name" --restart=unless-stopped "$docker_name":prod-v"$tag_version"


echo -e "############ Container started successfully ############"
exit 0