#!/usr/bin/python


from __future__ import (absolute_import, division, print_function)

from ..module_utils.constants.constants import API_BASE_HOST
DOCUMENTATION = r'''
---
module: delete_kafka_by_id 

short_description: This module deletes a Red Hat OpenShift Streams for Apache Kafka Instance by ID

version_added: "0.1.0-alpha"

short_description: This module deletes a Red Hat OpenShift Streams for Apache Kafka Instance by ID

options:
    kakfa_id:
        description: ID of the instance to be deleted
        required: true
        type: str
 
extends_documentation_fragment:
    - dimakis.rhosak_test.my_doc_fragment_name

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
    returned: in case of successful deletion 
message:
    description: The output error / exception message that is returned in the case the module generates an error / exception.
    type: dict
    returned: in case of error / exception
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
import auth.rhoas_auth as auth

def run_module():
    module_args = dict(
        kafka_id=dict(type='str', required=True),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    if module.check_mode:
        module.exit_json(**result)

    token = auth.get_access_token()
    
    configuration = rhoas_kafka_mgmt_sdk.Configuration(
        host = API_BASE_HOST,
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
