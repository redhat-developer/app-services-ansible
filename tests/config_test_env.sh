#!/bin/bash

# init python virtual environment
python3 -m venv env
source env/bin/activate

# install pip modules on virtual environment
pip install --upgrade pip
pip install -r ../requirements.txt
pip install pytest

# config python3.9 to run in mk-ci-tools container
mkdir -p /usr/local/opt/python@3.9/bin
cp /usr/bin/python3  /usr/local/opt/python@3.9/bin/python3.9

# set python interpreter on ansible config file
cat << EOT >> ansible.cfg
[defaults]
interpreter_python=/usr/app-services-ansible/tests/env/bin/python3.9
EOT

# build RHOSAK Ansible module collection from local files
ansible-galaxy collection build ../

# install the RHOAS ansible collection
ansible-galaxy collection install rhoas-rhoas-0.1.0-alpha.tar.gz

# deactivate python virtual environment
deactivate
