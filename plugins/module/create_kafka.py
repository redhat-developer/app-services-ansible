#!/usr/bin/python


from __future__ import (absolute_import, division, print_function)
import json
import time
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
        required: true 
        type: str
    region:
        description: Region of the Kafka instance
        required: true
        type: str
    reauthentication_enabled:
        description: Reauthentication enabled for the Kafka instance
        required: false
        type: bool
        default: true
    plan:
        description: Plan for the Kafka instance
        required: true
        type: str
    billing_cloud_account_id:
        description: Billing cloud account id for the Kafka instance
        required: false 
        type: str
    marketplace:
        description: Marketplace for the Kafka instance
        required: false 
        type: str
    billing_model:
        description: Billing model for the Kafka instance
        required: true 
        type: str
    instance_type:
        description: Instance type for the Kafka instance
        required: false
        type: str
 
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - redhat.rhosak.rhosak_doc_fragment

author:
    - Red Hat Developer
'''

EXAMPLES = r'''
# Pass in a Kakfa request object 
  - name: Create kafka
    redhat.rhoask.create_kafka:
      name: "kafka_name"
      instance_type: "x1"
      billing_model: "standard"
      cloud_provider: "aws"
      region: "us-east-1"
      plan: "developer.x1"
      billing_cloud_account_id: "123456789"
    register:
      kafka_req_resp 
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original kafka request payload that was passed in.
    type: dict
    returned: always
    sample: As can be found in the Red Hat App-Services Python SDK https://github.com/redhat-developer/app-services-sdk-python/blob/main/sdks/kafka_mgmt_sdk/docs/KafkaRequestPayload.md\#kafkarequestpayload
message:
    description: The output error / exception message that is returned in the case the module generates an error / exception.
    type: dict
    returned: in case of error / exception
kafka_req_resp:
    description: The response object from the Kafka_mgmt API.
    sample: As can be found in the Red Hat App-Services Python SDK https://github.com/redhat-developer/app-services-sdk-python/blob/main/sdks/kafka_mgmt_sdk/docs/KafkaRequest.md\#kafkarequest
    type: dict
    returned: when the module is successful
kafka_admin_url:
    description: The admin url for the Kafka instance.
    type: str
    returned: when the module is successful
kafka_id:
    description: The id of the Kafka instance.
    type: str
    returned: when the module is successful
kafka_state:
    description: The state of the Kafka instance.
    type: str
    returned: when the module is successful
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
        cloud_provider=dict(type='str', required=True),
        region=dict(type='str', required=True),
        reauthentication_enabled=dict(type='bool', required=False, default=True),
        plan=dict(type='str', required=True),
        billing_cloud_account_id=dict(type='str', required=False),
        marketplace=dict(type='str', required=False),
        billing_model=dict(type='str', required=True),
        instance_type=dict(type='str', required=False),
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
        kafka_req_resp=dict,
        kafka_id='',
        kafka_admin_url='',
        kafka_state=''
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
        host = "https://api.openshift.com",
        # for use with testing / mocking
        # host = "http://localhost:8000",
    )
    
    configuration.access_token = token["access_token"]
    
    def check_kafka_in_ready_state(kafka_mgmt_api_instance, retries = 10, backoff_in_seconds = 6):
        attempt = 0
        # Check for kafka_admin_url to be used to create topic
        while result['kafka_state'] != "ready":
            try:
                # Enter a context with an instance of the API client
                    kafka_id = result['kafka_id'] # str | The ID of record

                    # example passing only required values which don't have defaults set
                    try:
                        kafka_mgmt_api_response = kafka_mgmt_api_instance.get_kafka_by_id(kafka_id)
                        kafka_mgmt_api_response
                        result['kafka_admin_url'] = kafka_mgmt_api_response['admin_api_server_url']
                        result['kafka_state'] = kafka_mgmt_api_response['status']
                        result['kafka_admin_resp_obj'] = kafka_mgmt_api_response.to_dict()
                        
                    except rhoas_kafka_mgmt_sdk.ApiException as e:
                        rb = json.loads(e.body)
                        module.fail_json(msg=f'Failed to create new kafka instance with error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.')
            except:
                if attempt == retries:
                    raise
                sleep = (backoff_in_seconds * attempt)
                time.sleep(sleep)
                attempt += 1
                
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
                result['kafka_id'] = kafka_req_resp['id']
            check_kafka_in_ready_state(api_instance)
            
            result['changed'] = True
            # exit the module and return the state 
            module.exit_json(**result)
        except rhoas_kafka_mgmt_sdk.ApiException as e:
            rb = json.loads(e.body)
            module.fail_json(msg=f'Failed to create new kafka instance with error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.')

def main():
    run_module()


if __name__ == '__main__':
    main()
