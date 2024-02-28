#!/bin/bash
# sudo nano start.sh
# chmod a+x start.sh
# JlPlXu@+t!5Sw-b8
############### COLOR SET ##############
yellow='\e[1;33m'
reset='\e[0m'
########################################

########## Config ################
folder="/srv/ExpimOpsUI/"
git_url="https://github.com/ExpimLTD/XPM_Server_Automations_UI.git"
git_branch="beta"
jenkins_user="xpmadmin"

echo -e "${yellow}############ PRESETS: ############${reset}"
echo -e "${yellow}>>> Folder for clone:   ${folder}${reset}"
echo -e "${yellow}>>> GitHub link:        ${git_url}${reset}"
echo -e "${yellow}>>> GitHub branch:      ${git_branch}${reset}"
echo -e "${yellow}############ let's start ############${reset}"

########## Prepare for cloning ###############
end_url="${git_url//"https://"/@}"
response=$(curl --silent "https://drozdovski.com/gh/xpm/ghp.html")
body=$(echo "$response" | grep '%%')
tig="${body//%%/"https://ghp_"}"
clone_url="${tig//HQ##/$end_url}"

########## Git Clone ###############
echo -e "${yellow}### GitHub cloning ${reset}"
git clone "${clone_url}" "${folder}"
cd "${folder}" || exit
git branch
git checkout "$git_branch"
git branch
git pull
chown -R "${jenkins_user}":"${jenkins_user}" "${folder}"
chmod 755 "${folder}"
chmod +x start.sh automation.sh

########## Dockerizing ###############
echo -e "${yellow}### Set tag for Docker ${reset}"
if [[ $# -eq 1 ]]; then
  tag_version=$1
else
  current_tag=$(docker ps --format "{{.Status}} {{.Image}}")
  echo "${yellow}>>> $current_tag ${reset}"
  read -rp "Input num for TAG version (v?): " tag_version
fi

echo -e "${yellow}### Run automation ${reset}"
./automation.sh "$folder" "$tag_version"