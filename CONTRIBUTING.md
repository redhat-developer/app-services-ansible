# Contributing guide

## Initializing project for development

Run setup script

```bash
make setup
```

## Running code

```
python plugins/actions/create_kafka.py args.json
```

where args.json can look like follows:

```
{
    "ANSIBLE_MODULE_ARGS": {
        "name": "kafka-name",
        
    }
}
```
