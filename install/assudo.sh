#!/bin/bash

# Stop running interface, if it is running
systemctl stop buster-web.service

# Install packages
sudo apt update
sudo apt upgrade -y

# May not be necessary if the cloud-vm image works properly
apt install -y qemu-guest-agent

# Packages needed
apt install -y git python3.11-venv

# Create directory structure
mkdir -pm 777 /buster
rm -rf /buster/code          # Clear out existing code and venv
