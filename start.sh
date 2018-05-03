#!/bin/bash

CORD_VER=cord-4.1
DST=~/cord/build
TMP=/tmp/oai_scenario_backup/
mkdir /tmp/oai_scenario_backup

# Remove backup folder
rm -rf $TMP

# Backup all old files
cp $DST/docker_images.yml $TMP
cp $DST/../.repo/manifests/default.xml $TMP
cp $DST/platform-install/roles/cord-profile/templates/public-net.yaml.j2 $TMP

# Copy new files into our target
cp docker_images.yml $DST/
cp manifest.xml $DST/../.repo/manifests/default.xml
cp mcord-oai.yml $DST/platform-install/profile_manifests/
cp mcord-oai-virtual.yml $DST/podconfig/
cp public-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/
cp oai-net.yaml.j2 $DST/platform-install/roles/cord-profile/templates/
cp mcord-oai-services.yml.j2 $DST/platform-install/roles/cord-profile/templates
cp mcord-oai-service-graph.yml.j2 $DST/platform-install/roles/cord-profile/templates

# Use custom version of vhss, vmme instead official
cd ~/cord/orchestration/xos_services
rm -rf vbbu vhss vmme vspgwc vspgwu
git clone https://github.com/aweimeow/vBBU vbbu
git clone https://github.com/aweimeow/vMME vmme
git clone https://github.com/aweimeow/vHSS vhss
git clone https://github.com/aweimeow/vspgwc vspgwc
git clone https://github.com/aweimeow/vspgwu vspgwu

# Checkout to target branch
for var in "vbbu" "vhss" "vmme" "vspgwc" "vspgwu"; do
    cd $var;
    git remote add opencord https://github.com/aweimeow/$var.git;
    git checkout ciab-4.1;
    git checkout -b $CORD_VER;
    mkdir .git/refs/remotes/opencord/;
    echo $(git log --format="%H" -n 1) > .git/refs/remotes/opencord/$CORD_VER;
    cd ..;
done
