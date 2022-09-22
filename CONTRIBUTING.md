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

where create_kafka.json contains input arguments. For example:

```json
{
    "ANSIBLE_MODULE_ARGS": {
        "name": "kafka-name",
        
    }
}
```
## Testing with Ansible Playbooks
A further way to run / test the code locally is with the use of an [Ansible Playbook](https://docs.ansible.com/ansible/latest/dev_guide/developing_modules_general.html#verifying-your-module-code-in-a-playbook). 
To do so the following steps are required:

- run `make local-dev` to create a local Ansible Library collection in the root of the project. This will copy existing modules to the collection. 
- a playbook can be created in the root of the project and ran via the `ansible-playbook` command. For example:

```bash
ansible-playbook 'playbook.yaml' -vvv
```

where playbook.yml contains the following:

```yaml
---
- name: Create_kafka test
  hosts: localhost
  connection: local
  gather_facts: true
  tasks:
    - name: Create Kafka
      create_kafka:
        name: kafka-name
```

**Note:**
The `create_kafka` command in the task needs to be the **Fully Qualified Name** of the module for collection developemnet i.e. `redhat.rhoask.create_kafka`.


```yaml
...
  gather_facts: true
  tasks:
    - name: Create Kafka
      redhat.rhosak.create_kafka:
        name: kafka-name
...
```
Just remember to add the module back to the collection when you are done with the testing againsta a playbook.
