#!/bin/bash

CORD_VER='cord-5.0'
BRANCH=$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
DST=~/cord

# Copy new files into our target
cp docker_images.yml $DST/build
cp manifest.xml $DST/.repo/manifests/default.xml
cp mcord-oai.yml $DST/orchestration/profiles/mcord/
cp mcord-oai-physical.yml $DST/orchestration/profiles/mcord/podconfig/
cp public-net.yaml.j2 $DST/build/platform-install/roles/cord-profile/templates/
cp oai-net.yaml.j2 $DST/build/platform-install/roles/cord-profile/templates/
cp mcord-oai-services.yml.j2 $DST/build/platform-install/roles/cord-profile/templates/
cp mcord-oai-service-graph.yml.j2 $DST/build/platform-install/roles/cord-profile/templates/

# Use custom version of services instead official
cd ~/cord/orchestration/xos_services

for var in "vbbu" "vhss" "vmme" "vspgwc" "vspgwu"; do
    rm -rf $var;
    git clone https://github.com/aweimeow/$var.git $var;
    cd $var;
    git remote add opencord https://github.com/aweimeow/$var.git;
    git checkout $BRANCH;
    git checkout -b $CORD_VER;
    cd ..;
done
