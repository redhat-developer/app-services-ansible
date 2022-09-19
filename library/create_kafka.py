#!/usr/bin/python


from __future__ import (absolute_import, division, print_function)
from sys import api_version
__metaclass__ = type

DOCUMENTATION = r'''
---
module: create_kafka

short_description: Create Red Hat OpenShift Streams for Apache Kafka Instance

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.1.0"

description: Create Red Hat OpenShift Streams for Apache Kafka Instance

options:
    name:
        description: Name of the Kafka instance
        required: true
        type: str
    cloud_provider:
        description: Cloud provider for the Kafka instance
        required: false
        type: str
        default: aws
    region:
        description: Region of the Kafka instance
        required: false
        type: str
        default: eu-west-1
    reauthentication_enabled:
        description: Reauthentication enabled for the Kafka instance
        required: false
        type: bool
        default: true
    plan:
        description: Plan for the Kafka instance
        required: false
        type: str
        default: ""
    billing_cloud_account_id:
        description: Billing cloud account id for the Kafka instance
        required: false
        type: str
        default: ""
    marketplace:
        description: Marketplace for the Kafka instance
        required: false
        type: str
        default: ""
    billing_model:
        description: Billing model for the Kafka instance
        required: false
        type: str
        default: marketplace
    instance_type:
        description: Instance type for the Kafka instance
        required: false
        type: str
        default: developer
 
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Red Hat Developer
'''

EXAMPLES = r'''
# Pass in a message
  - name: Create kafka
    create_kafka:
      name: "struttin"
    register:
      kafka_req_resp 

 
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original kafka request payload that was passed in.
    type: dict
    returned: always
    sample: "invocation": {
        "module_args": {
            "billing_cloud_account_id": "",
            "billing_model": "marketplace",
            "cloud_provider": "aws",
            "instance_type": "developer",
            "marketplace": "",
            "name": "struttin",
            "plan": "",
            "reauthentication_enabled": "True",
            "region": "eu-west-1"
        }
message:
    description: The output error / exception message that is returned in the case the module generates an error / exception.
    type: dict
    returned: in case of error / exception
kafka_req_resp:
    description: The response object from the Kafka_mgmt API.
    "changed": true,
        "failed": false,
        "kafka_req_resp": {
            "admin_api_server_url": "http://localhost:8000/data/kafka",
            "billing_cloud_account_id": "",
            "billing_model": "marketplace",
            "bootstrap_server_host": "localhost:8000",
            "browser_url": "http://localhost:8080/calbu9ccff6bdd4jsg30/dashboard",
            "cloud_provider": "aws",
            "created_at": "2020-10-05T12:51:24.053142+00:00",
            "egress_throughput_per_sec": "1Mi",
            "expires_at": "2022-06-18T05:27:01.816619+00:00",
            "href": "/api/kafkas_mgmt/v1/kafkas/68Pr91QnNwW6Wis7J7jxM",
            "id": "68Pr91QnNwW6Wis7J7jxM",
            "ingress_throughput_per_sec": "1Mi",
            "instance_type": "developer",
            "instance_type_name": "Trial",
            "kafka_storage_size": "10Gi",
            "kind": "Kafka",
            "marketplace": "",
            "max_connection_attempts_per_sec": 50.0,
            "max_data_retention_period": "P14D",
            "max_partitions": 100.0,
            "multi_az": false,
            "name": "struttin",
            "owner": "dsaridak",
            "plan": "",
            "reauthentication_enabled": true,
            "region": "us-east-1",
            "size_id": "x1",
            "status": "ready",
            "total_max_connections": 100.0,
            "updated_at": "2020-10-05T12:56:36.362208+00:00",
            "version": "3.0.1"
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
from rhoas_kafka_mgmt_sdk.model.kafka_request_payload import KafkaRequestPayload
import auth.rhoas_auth as auth

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        cloud_provider=dict(type='str', required=False, default='aws'),
        region=dict(type='str', required=False, default="eu-west-1"),
        reauthentication_enabled=dict(type='bool', required=False, default=True),
        plan=dict(type='str', required=False, default=""),
        billing_cloud_account_id=dict(type='str', required=False, default=""),
        marketplace=dict(type='str', required=False, default=""),
        billing_model=dict(type='str', required=False, default="marketplace"),
        instance_type=dict(type='str', required=False, default="developer"),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message='',
        kafka_req_resp=dict
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    # module.check_mode = False
    if module.check_mode:
        module.exit_json(**result)

    token = auth.get_access_token()
    
    configuration = rhoas_kafka_mgmt_sdk.Configuration(
        # host = "https://api.openshift.com",
        # for use with testing / mocking
        host = "http://localhost:8000",
    )
    
    configuration.access_token = token["access_token"]
    # Enter a context with an instance of the API client
    with rhoas_kafka_mgmt_sdk.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = default_api.DefaultApi(api_client)
        _async = True # bool | Perform the action in an asynchronous manner
        kafka_request_payload = KafkaRequestPayload(
            cloud_provider=module.params['cloud_provider'],
            name=module.params['name'],
            region=module.params['region'],
            reauthentication_enabled=True,
            plan=module.params['plan'],
            billing_cloud_account_id=module.params['billing_cloud_account_id'],
            marketplace=module.params['marketplace'],
            billing_model=module.params['billing_model'],
        ) 
        try:
            result['original_message'] = module.params
            api_response = api_instance.create_kafka(_async, kafka_request_payload, async_req=True)
            kafka_req_resp = api_response.get(2000)

            if kafka_req_resp['status'] == 'accepted' or kafka_req_resp['status'] == 'ready' or kafka_req_resp['status'] == 'provisioning':
                result['kafka_req_resp'] = kafka_req_resp.to_dict()
                result['changed'] = True
            
            # exit the module and return the state 
            module.exit_json(**result)
        except rhoas_kafka_mgmt_sdk.ApiException as e:
            print("Exception when calling DefaultApi -> create_kafka: %s\n" % e)
            result['message'] = e
            module.fail_json(msg='Failed to create kafka instance', **result)

def main():
    run_module()


if __name__ == '__main__':
    main()
