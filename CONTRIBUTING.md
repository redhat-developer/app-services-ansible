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

