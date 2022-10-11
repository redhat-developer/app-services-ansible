# Red Hat Application Services Ansible Collection

Ansible Collection for Red Hat Application Services

## Installing collection

```shell
ansible-galaxy collection install redhat_cloud.services
```

This collection will work best if used in a Python virtual environment. To create and activate a Python virtual environment, run the following command:

```shell
python3 -m venv rhoas
. rhoas/bin/activate
```

This collection requires some additional dependencies to be installed:

```shell
pip install rhoas-sdks --force-reinstall
```

