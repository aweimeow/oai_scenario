#!/bin/bash

CORD_VER='cord-5.0'
BRANCH='master' #$(git branch | sed -n -e 's/^\* \(.*\)/\1/p')
DST=~/cord

# Copy new files into our target
cp docker_images.yml $DST/build
cp mcord-oai.yml $DST/orchestration/profiles/mcord/

# Copy podconfig
cp mcord-oai-virtual.yml $DST/orchestration/profiles/mcord/podconfig/
cp mcord-oai-physical.yml $DST/orchestration/profiles/mcord/podconfig/

# Copy Template files
cp mcord-oai-services.yml.j2 $DST/orchestration/profiles/mcord/templates/
cp mcord-oai-address-manager.yml.j2 $DST/orchestration/profiles/mcord/templates/
cp vtn-service.yaml.j2 $DST/orchestration/profiles/mcord/templates/
cp mcord-oai-test-playbook.yml $DST/orchestration/profiles/mcord/test/

# Use custom version of services instead official
cd ~/cord/orchestration/xos_services

for var in "vbbu" "vhss" "vmme" "vspgwc" "vspgwu" "epc-service"; do
    rm -rf $var;
    git clone https://github.com/aweimeow/$var.git $var;
    cd $var;
    git remote add opencord https://github.com/aweimeow/$var.git;
    git remote add dev git@github.com:aweimeow/$var.git;
    git checkout $BRANCH;
    git checkout -b $CORD_VER;
    mkdir .git/refs/remotes/opencord/;
    echo $(git log --format="%H" -n 1) > .git/refs/remotes/opencord/$CORD_VER;
    cd ..;
done
