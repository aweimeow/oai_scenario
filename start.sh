#!/bin/bash

DST=~/cord/build
TMP=/tmp/oai_scenario_backup/
mkdir /tmp/oai_scenario_backup

# Backup all old files
cp $DST/docker_images.yml $TMP
cp $DST/../.repo/manifests/default.xml $TMP
cp -r $DST/platform-install/roles/cord-profile/templates $TMP

# Copy new files into our target
cp docker_images.yml $DST/
cp manifest.xml $DST/../.repo/manifests/default.xml
cp mcord-oai.yml $DST/platform-install/profile_manifests/
cp mcord-oai-virtual.yml $DST/podconfig/
cp mcord-oai-services.yml.j2 $DST/platform-install/roles/cord-profile/templates
cp mcord-oai-service-graph.yml.j2 $DST/platform-install/roles/cord-profile/templates
cp ./oai-net-template/public-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/
cp ./oai-net-template/oai-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/
cp ./oai-net-template/oai-s1mme-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/
cp ./oai-net-template/oai-s1u-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/
cp ./oai-net-template/s6a-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/
cp ./oai-net-template/s11-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/

# Use custom version of vhss, vmme instead official
cd ~/cord/orchestration/xos_services

for var in "vmme" "vhss" "oaispgw" "epc-service"; do
  if [ -d "$var" ]; then
    rm -rf $var
  fi
done

git clone https://github.com/jiahchen/vMME vmme
git clone https://github.com/jiahchen/vHSS vhss
git clone https://github.com/jiahchen/oaispgw oaispgw
git clone https://github.com/jiahchen/epc-service epc-service

# Checkout to target branch
for var in "vmme" "vhss" "oaispgw" "epc-service"; do
    cd $var;
    git remote add opencord https://github.com/jiahchen/$var.git;
    git checkout cord-4.1;
    git pull opencord cord-4.1;
    cd ..;
done
