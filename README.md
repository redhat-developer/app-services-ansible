# Red Hat Application Services Ansible Collection

Ansible Collection for Red Hat Application Services

## Installing collection

```shell
ansible-galaxy collection install rhoas.rhoas
```

This collection will work best if it used within a Python virtual environment. To create and activate a Python virtual environment, run the following command:

```shell
python3 -m venv rhoas
. rhoas/bin/activate
```

This collection requires some additional dependencies to be installed:

```shell
pip install rhoas-sdks --force-reinstall
pip install python-dotenv
```

## Using collection

An example Ansible playbook which demonstrates the RHOAS modules abilities can be [found here](https://github.com/redhat-developer/app-services-ansible/blob/2a47a44a92d871f99bba2ced38ff770f00e3c3da/run_rhosak_test.yml).

```shell
ansible-galaxy collection install rhoas.rhoas
```

The playbook and all modules require an 'OFFLINE_TOKEN' to be used with for authentication with the Red Hat OpenShift Application Services API. The token can be passed in like this:

```yaml
...
  tasks:
  - name: Create kafka
    rhoas.rhoas.create_kafka:
      name: "unique-kafka-name"
      openshift_offline_token: "OFFLINE_TOKEN"
...
```

If the token is not passed in, the module will attempt to read it from the environment variable `OFFLINE_TOKEN`. This token is used to authenticate the user. The token is an OpenShift Token and can be found [here](https://console.redhat.com/openshift/token)

Two further environment variables are used for the collection to work. These environment variables can be placed in a `.env` file.
They are:

- `API_BASE_HOST` - The base host for the API. This is the base URL for the API. For example, `https://api.openshift.com`
- `SSO_BASE_HOST` - The base host for the SSO. This is the base URL for the SSO. For example, `https://sso.redhat.com/auth/realms/redhat-external`

If neither of these environment variables are set, the collection will default to the URLs as noted in the examples.

The collection can be used in a playbook like this:

```shell
ansible-playbook run_rhosak_test.yml
```

This playbook, if run as is, will do the following:

- Create a Red Hat OpenShift Streams for Apache Kafka instance.
- Create a Service Account.
- Create an Access Control List (ACL) for the Service Account with some default values and bind that ACL to the Kafka instance and Service Account.
- Create two Kafka topics.
    - One with some examples of different configurations available.
    - One with default values as provided by the API.

The playbook will then proceed to delete the created resources and as such, some alteration of the playbook will be required to keep the resources created.
