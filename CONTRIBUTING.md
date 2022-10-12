# Contributing guide

## Initializing project for development

Run setup script

```bash
make setup
```


## Running code

```bash
python3 plugins/module/create_kafka.py ./tests/create_kafka.json
```

Where `create_kafka.json` contains input arguments. For example:

```json
{
    "ANSIBLE_MODULE_ARGS": {
        "name": "kafka-name",
        
    }
}
```

## Using collection

All modules require an 'OFFLINE_TOKEN' to be used with for authentication with the Red Hat OpenShift Application Services API. The token can be passed in like this:

```yaml
...
  tasks:
  - name: Create kafka
    redhat_developer.rhoas.create_kafka:
      name: "unique_kafka_name"
      openshift_offline_token: "OFFLINE_TOKEN"
...
```

If the token is not passed in, the module will attempt to read it from the environment variable `OFFLINE_TOKEN`. This token is used to authenticate the user. The token is an OpenShift Cluster Manager API Token and can be found [here](https://console.redhat.com/openshift/token)

Two further environment variables are used for the collection to work. These environment variables can be placed in a `.env` file.
They are:

- `API_BASE_HOST` - The base host for the API. This is the base URL for the API. For example, `https://api.openshift.com`
- `SSO_BASE_HOST` - The base host for the SSO. This is the base URL for the SSO. For example, `https://sso.redhat.com/auth/realms/redhat-external`

If neither of these environment variables are set, the collection will default to the URLs as noted in the examples.

## Testing with Ansible Playbooks

A further way to run / test the code locally is with the use of an [Ansible Playbook](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#verifying-your-module-code-in-a-playbook).

To do so the following steps are required:

- Run `make local-dev` to create a local Ansible Library collection in the root of the project. This will copy existing modules to the collection.
- A playbook can be created in the root of the project and ran via the `ansible-playbook` command. For example:

```bash
ansible-playbook 'playbook.yaml' -vvv
```

where playbook.yml contains the following:

```yaml
---
- name: Create_kafka test
  hosts: localhost
  connection: local
  gather_facts: false 
  tasks:
    - name: Create Kafka
      create_kafka:
        name: kafka-name
```

**Note:**
The `create_kafka` command in the task needs to be the **Fully Qualified Name** of the module for collection development i.e. `redhat_developer.rhoas.create_kafka`.

```yaml
...
  gather_facts: false
  tasks:
    - name: Create Kafka
      redhat.rhosak.create_kafka:
        name: kafka-name
...
```

Just remember to add the module back to the collection when you are done with the testing against a playbook.
