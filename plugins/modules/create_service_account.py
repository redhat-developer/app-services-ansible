#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from __future__ import (absolute_import, division, print_function)
import os

from ..module_utils.constants.constants import SSO_BASE_HOST
from dotenv import load_dotenv

DOCUMENTATION = r'''
---
module: create_service_account

short_description: Create a Service Account for use with Red Hat Openshift Application Services 

version_added: "0.1.0-alpha"

description: Create a Service Account for use with Red Hat Openshift Application Services 

options:
    name:
        description: Name of the service account
        required: true
        type: str
    description:
        description: Description of the service account
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
# Pass in a message
  - name: Create Service Account
    create_service_account:
      name: "service_account_name"
      description: "This is a description of the service account"
      openshift_offline_token: "OPENSHIFT_CLUSTER_MANAGER_API_OFFLINE_TOKEN"
    register:
      srvce_acc_resp_obj
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original dict with params that were passed in.
    type: dict
    returned: always
message:
    description: The output error / exception message that is returned in the case the module generates an error / exception.
    type: dict
    returned: In case of error / exception.
srvce_acc_resp_obj: 
    description: The service account response object.
    type: dict
    returned: If service account is created successfully.
    sample: Client ID and Client Secret of the service account. 
client_id:
    description: The client id of the service account.
    type: str
    returned: If service account is created successfully.
client_secret:
    description: The client secret of the service account.
    type: str
    returned: If service account is created successfully.
env_url_error:
    description: The error message returned if no environment variable is passed for the BASE_HOST URL.
    type: str
    returned: If the module uses default url instead of passed environment variable.
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_service_accounts_mgmt_sdk
import auth.rhoas_auth as auth
from rhoas_service_accounts_mgmt_sdk.api import service_accounts_api
from rhoas_service_accounts_mgmt_sdk.model.service_account_create_request_data import ServiceAccountCreateRequestData

load_dotenv(".env")

def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        description=dict(type='str', required=True),
        openshift_offline_token=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        srvce_acc_resp_obj=dict,
        client_id='',
        client_secret='',
        env_url_error='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    if module.check_mode:
        result['message'] = 'Check mode is not supported'
        module.exit_json(**result)

    if module.params['openshift_offline_token'] is None or module.params['openshift_offline_token'] == '':
        token = auth.get_access_token(offline_token=None)
    else: 
        token = auth.get_access_token(module.params['openshift_offline_token'])
   
    sso_base_host = os.getenv("SSO_BASE_HOST") 
    if sso_base_host is None:
        result['message'] = 'cannot find SSO_BASE_HOST in .env file'
        sso_base_host = SSO_BASE_HOST
   
    configuration = rhoas_service_accounts_mgmt_sdk.Configuration(
            host = sso_base_host,    
    )
    
    configuration.access_token = token["access_token"]

    with rhoas_service_accounts_mgmt_sdk.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = service_accounts_api.ServiceAccountsApi(api_client)
        try:
            service_account_create_request_data = ServiceAccountCreateRequestData(
                name=module.params['name'],
                description=module.params['description'],
            ) 
            api_response = api_instance.create_service_account(service_account_create_request_data)
            
            result['srvce_acc_resp_obj'] = {
                "client_id" : api_response['client_id'],
                'client_secret': api_response['secret'],
            }
            result['client_id'] = api_response['client_id']
            result['client_secret'] = api_response['secret']
            
            result['changed'] = True

            module.exit_json(**result)
        except rhoas_service_accounts_mgmt_sdk.ApiException as e:
            result['message'] = e.body
            module.fail_json(msg='Failed to create kafka instance, API exception', **result)
        except Exception as e:
            result['message'] = e
            module.fail_json(msg='Failed to create kafka instance, with general exception', **result)   

def main():
    run_module()

if __name__ == '__main__':
    main()
