#!/usr/bin/python


from __future__ import (absolute_import, division, print_function)
import os

from ..module_utils.constants.constants import API_BASE_HOST
from dotenv import load_dotenv

DOCUMENTATION = r'''
---
module: delete_kafka_by_id 

short_description: This module deletes a Red Hat OpenShift Streams for Apache Kafka Instance by ID.

version_added: "0.1.0-alpha"

short_description: This module deletes a Red Hat OpenShift Streams for Apache Kafka Instance by ID.

options:
    kakfa_id:
        description: ID of the instance to be deleted.
        required: true
        type: str
    openshift_offline_token:
        description: `openshift_offline_token` is the OpenShift Cluster Manager API Offline Token that is used for authentication to enable communication with the Kafka Management API. If not provided, the `OFFLINE_TOKEN` environment variable will be used.
        required: false
        type: str
 
extends_documentation_fragment:
    - rhoas.rhoas.rhoas_doc_fragment

author:
    - Red Hat Developer
'''

EXAMPLES = r'''
  - name: Delete kafka instance by ID
    delete_kafka_by_id:
      kafka_id: "kafka_id"
'''

RETURN = r'''
original_message:
    description: The original kafka ID set for deletion that was passed in.
    type: dict
    returned: In case of successful deletion.
message:
    description: The output error / exception message that is returned in the case the module generates an error / exception.
    type: dict
    returned: In case of error / exception.
env_url_error:
    description: The error message returned if no environment variable is passed for the BASE_HOST URL.
    type: str
    returned: If the module uses default url instead of passed environment variable.
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
import auth.rhoas_auth as auth

load_dotenv(".env")

def run_module():
    module_args = dict(
        kafka_id=dict(type='str', required=True),
        openshift_offline_token=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        env_var_error='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    if module.check_mode:
        result['message'] = 'Check mode is not supported.'
        module.exit_json(**result)

    if module.params['openshift_offline_token'] is None or module.params['openshift_offline_token'] == '':
        token = auth.get_access_token(offline_token=None)
    else:
        token = auth.get_access_token(module.params['openshift_offline_token'])
    
    api_base_host = os.getenv("API_BASE_HOST") 
    if api_base_host is None:
        result['env_url_error'] = 'cannot find API_BASE_HOST in .env file, using default url values instead'
        api_base_host = API_BASE_HOST
    configuration = rhoas_kafka_mgmt_sdk.Configuration(
        host = api_base_host
    )
    
    configuration.access_token = token["access_token"]
    
    with rhoas_kafka_mgmt_sdk.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = default_api.DefaultApi(api_client)
        _async = True # bool | Perform the action in an asynchronous manner
        id = module.params['kafka_id'] # str | The ID of the Kafka instance to be deleted.
        try:
            del_resp = api_instance.delete_kafka_by_id(id, _async, async_req=True)
            del_resp = del_resp.get()
            result['original_message'] = f'Kafka instance with ID: {id} set for deletion'
            result['message'] = "Kafka instance deleted"
            result['changed'] = True
            # exit the module and return the state 
            module.exit_json(**result)
        except rhoas_kafka_mgmt_sdk.ApiException as e:
            print("Exception when calling DefaultApi -> delete_kafka_by_id: %s\n" % e)
            result['message'] = e
            module.fail_json(msg='Failed to delete kafka instance', **result)
        except Exception as e:
            result['message'] = e
            module.fail_json(msg='Failed to delete kafka instance', **result)

def main():
    run_module()


if __name__ == '__main__':
    main()
