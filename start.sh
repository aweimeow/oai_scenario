#! /usr/bin/bash

PATH=~/cord/build
TMP=/tmp/oai_scenario_backup/
mkdir /tmp/oai_scenario_backup

# Backup all old files
cp $PATH/docker_images.yml $TMP
cp $PATH/../.repo/manifests/default.xml $TMP
cp $PATH/platform-install/roles/cord-profile/templates/public-net.yaml.j2 $TMP

# Copy new files into our target
cp docker_images.yml $PATH/
cp manifest.xml $PATH/../.repo/manifests/default.xml
cp mcord-oai.yml $PATH/platform-install/profile_manifests/
cp mcord-oai-virtual.yml $PATH/podconfig/
cp public-net.yaml.j2 $PATH/platform-install/roles/cord-profile/templates/
cp oai-net.yaml.j2 $PATH/platform-install/roles/cord-profile/templates/
cp mcord-oai-services.yml.j2 $PATH/platform-install/roles/cord-profile/templates
