#!/bin/bash

TESTS_PATH="${TESTS_PATH:-"$(cd -- "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"}"
REPO_ROOT="$TESTS_PATH/.."

# init python virtual environment
python3 -m venv $TESTS_PATH/venv
source $TESTS_PATH/venv/bin/activate

# install pip modules on virtual environment
pip install --upgrade pip
pip install -r $REPO_ROOT/requirements.txt
pip install pytest

# set python interpreter on ansible config file
rm $TESTS_PATH/ansible.cfg
cat << EOT >> $TESTS_PATH/ansible.cfg
[defaults]
interpreter_python=/usr/app-services-ansible/tests/venv/bin/python3.9
EOT

# build RHOSAK Ansible module collection from local files
ansible-galaxy collection build --output-path $TESTS_PATH $REPO_ROOT

# install the RHOAS ansible collection
GALAXY_YAML="$REPO_ROOT/galaxy.yml"
NAMESPACE=$(cat $GALAXY_YAML | yq '.namespace')
NAME=$(cat $GALAXY_YAML | yq '.name')
VERSION=$(cat $GALAXY_YAML | yq '.version')
ansible-galaxy collection install $TESTS_PATH/$NAMESPACE-$NAME-$VERSION.tar.gz

# deactivate python virtual environment
deactivate
