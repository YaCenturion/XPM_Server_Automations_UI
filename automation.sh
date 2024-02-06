#!/bin/bash
# example: bash automation.sh . 73
# 73 - just number tag version for docker when running container

############### COLOR SET ##############
yellow='\e[1;33m'
reset='\e[0m'
green='\033[0;32m'
########################################

docker ps -a
docker stop expim-tools
docker rm expim-tools
docker container prune -f

if [[ $# -eq 2 ]]; then
  folder=$1
  num_version=$2
  tag_version="${num_version}"

  if [ "$folder" == "." ]; then
    # Set folder to the current working directory if the first argument is "."
    folder=$(pwd)
  fi

else
  folder="/srv/SandBox"
  tag_version="_no_revision"

  echo -e "${yellow}############ WARNING! ############${reset}"
  echo -e "${yellow}FOLDER: $folder and TAG: $tag_version${reset}"
  echo -e "${yellow}############# ###### #############${reset}"
fi

echo -e "${yellow}############ Build container ############${reset}"
docker build -t expim-tools:prod-v"$tag_version" .

echo -e "${yellow}############ Checking 172.27.0.0/16 docknet ############${reset}"
NETWORK_NAME="docknet"
if docker network inspect $NETWORK_NAME &>/dev/null; then
  echo "Network '$NETWORK_NAME' already exist."
else
    # Создание сети
    if docker network create --subnet=172.27.0.0/16 $NETWORK_NAME; then
        echo "Network '$NETWORK_NAME' created."
    else
        echo "Error when try create network: '$NETWORK_NAME'."
        exit 1
    fi
fi

echo -e "${yellow}############ Run container ############${reset}"
docker run -d -e APP_BUILD_VERSION="$tag_version" -v "$folder"/instance:/app/instance -p 80:5000 --network=docknet --name expim-tools --restart=unless-stopped expim-tools:prod-v"$tag_version"

echo -e "${green}############ Container started successfully ############${reset}"
exit 0