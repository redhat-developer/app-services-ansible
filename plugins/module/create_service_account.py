#!/usr/bin/python


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: create_service_account

short_description: Create Service Account for use with Red Hat Openshift Application Services 

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.1.0"

description: Create Service Account for use with Red Hat Openshift Application Services 

options:
    name:
        description: Name of the service account
        required: true
        type: str
 
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
    - my_namespace.my_collection.my_doc_fragment_name

author:
    - Red Hat Developer
'''

EXAMPLES = r'''
# Pass in a message
  - name: Create Service Account
    create_service_account:
      name: "struttin-jeeves"
      description: "struttin-jeeves service account"
    register:
      srvce_acc_resp_obj
  - name: Debug service account
    debug:
      msg: "{{ srvce_acc_resp_obj }}"

 
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original dict with params that was passed in.
    type: dict
    returned: always
    sample: "invocation": {
        "module_args": {
            "description": "struttin-jeeves service account",
            "name": "struttin-jeeves"
        }
    },
message:
    description: The output error / exception message that is returned in the case the module generates an error / exception.
    type: dict
    returned: in case of error / exception
srvce_acc_resp_obj: 
    description: The service account response object
    type: dict
    returned: when service account is created successfully
    sample: 
        "srvce_acc_resp_obj"{
            "client_id": "cfb4300f-be22-490a-913d-678b0da9f833",
            "client_secret": "5aPOeYmE40ztvsOkFwzNZ6Y7l1vA9m7y"
    }

'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_service_accounts_mgmt_sdk
import auth.rhoas_auth as auth
from rhoas_service_accounts_mgmt_sdk.api import service_accounts_api
from rhoas_service_accounts_mgmt_sdk.model.service_account_create_request_data import ServiceAccountCreateRequestData

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', required=False),
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
        srvce_acc_resp_obj=dict
        
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
    
    configuration = rhoas_service_accounts_mgmt_sdk.Configuration(
        host = "https://sso.redhat.com/auth/realms/redhat-external",
        # uncomment this next line for local testing using the mock server
        # host = "http://localhost:8000",
    )
    configuration.access_token = token["access_token"]

    
    # Enter a context with an instance of the API client
    with rhoas_service_accounts_mgmt_sdk.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = service_accounts_api.ServiceAccountsApi(api_client)
        try:
            service_account_create_request_data = ServiceAccountCreateRequestData(
                name=module.params['name'],
                description=module.params['description'],
            ) 
            api_response = api_instance.create_service_account(service_account_create_request_data)
            
            print('type api_response', api_response)
            print('client_id == ', api_response['client_id'])
            result['srvce_acc_resp_obj'] = {
                "client_id" : api_response['client_id'],
                'client_secret': api_response['secret'],
            }
            
            result['changed'] = True

            # in the event of a successful module execution, you will want to
            # simple AnsibleModule.exit_json(), passing the key/value results
            
            module.exit_json(**result)
        except rhoas_service_accounts_mgmt_sdk.ApiException as e:
            print("Exception when calling ServiceAccountsApi->create_service_account: %s\n" % e)
            result['message'] = e
            module.fail_json(msg='Failed to create kafka instance', **result)

def main():
    run_module()


if __name__ == '__main__':
    main()
