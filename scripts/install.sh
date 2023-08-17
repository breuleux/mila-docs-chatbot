#!/bin/bash

HERE=$(dirname "${BASH_SOURCE}" | xargs realpath)

# Stop running interface, if it is running
systemctl stop buster-web.service

set -e

# Install packages
apt update -yqq
apt upgrade -yqq

# May not be necessary if the cloud-vm image works properly
apt install -yqq qemu-guest-agent

# Packages needed
apt install -yqq git python3.11-venv

# Create directory structure
mkdir -pm 777 /buster
rm -rf /buster/code          # Clear out existing code and venv
cp -r $HERE/.. /buster/code
cd /buster/code

# Set up virtual environment
python3.11 -m venv venv
source venv/bin/activate
pip install -U pip
pip install poetry

# Install buster
pip install -e .

chown -R buster /buster
chgrp -R buster /buster

cp -f $HERE/../systemd/*.service /etc/systemd/system/
cp -f $HERE/../systemd/*.timer /etc/systemd/system/

systemctl daemon-reload

systemctl start buster-regen-docs.timer
systemctl enable buster-regen-docs.timer

systemctl start buster-web.service
systemctl enable buster-web.service
