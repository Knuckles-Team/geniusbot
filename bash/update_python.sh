#!/bin/bash

# This script will update all installed Python packages and dependencies to ther latest version.
# Update Packages
sudo yum -y update
# Update PIP
sudo python3 -m pip install --upgrade pip
sudo python3.8 -m pip install --upgrade pip
# Install Python Depedencies
sudo yum install gcc python3-devel python38-devel openssl-devel tcl-thread xz-libs bzip2-devel libffi-devel python3-tkinter python38-tkinter -y 
# Update all Packages
sudo python3 -m pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
sudo python3.8 -m pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1  | xargs -n1 pip install -U
