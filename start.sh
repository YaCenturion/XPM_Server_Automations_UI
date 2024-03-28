#!/bin/bash
# sudo chmod a+x start.sh

########## Config ################
tkn="https://drozdovski.com/gh/xpm/ghp.html"
deploy_folder="/srv/ExpimOpsUI/"
git_url="https://github.com/ExpimLTD/XPM_Server_Automations_UI.git"
git_branch="master"
jenkins_user="xpmadmin"
docker_name="expim-ops"

echo -e "############ PRESETS: ############"
echo -e ">>> Folder for clone:   ${deploy_folder}"
echo -e ">>> GitHub link:        ${git_url}"
echo -e ">>> GitHub branch:      ${git_branch}"
echo -e "############ let's start ############"

########## Prepare for cloning ###############
end_url="${git_url//"https://"/@}"
response=$(curl --silent "${tkn}")
body=$(echo "$response" | grep '%%')
tig="${body//%%/"https://ghp_"}"
clone_url="${tig//HQ##/$end_url}"

########## Git Clone ###############
echo -e "### GitHub cloning"
git clone "${clone_url}" "${deploy_folder}"
cd "${deploy_folder}" || exit
git branch
git checkout "$git_branch"
git branch
git pull
chown -R "${jenkins_user}":"${jenkins_user}" "${deploy_folder}"
chmod 755 "${deploy_folder}"
chmod +x start.sh automation.sh

########## Dockerizing ###############
echo -e "### Set tag for Docker"
if [[ $# -eq 1 ]]; then
  tag_version=$1
else
  current_tag=$(docker ps --format "{{.Status}} {{.Image}}")
  echo ">>> $current_tag "
  read -rp "Input num for TAG version (v?): " tag_version
fi

echo -e "### Run automation"
./automation.sh "$deploy_folder" "$docker_name" "$tag_version" "$git_branch"