#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from __future__ import (absolute_import, division, print_function)
import json
import os

from ..module_utils.constants.constants import SSO_BASE_HOST
from dotenv import load_dotenv

DOCUMENTATION = r'''
---
module: delete_service_account_by_id

short_description: Delete a Service Account for use with Red Hat Openshift Application Services.

version_added: "0.1.0-alpha"

description: Delete a Service Account for use with Red Hat Openshift Application Services.

options:
    service_account_id:
        description: ID of the Service Account
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
  - name: Delete Service Account
    delete_service_account_by_id:
        service_account_id: "SERVICE_ACCOUNT_ID"
        openshift_offline_token: "OPENSHIFT_CLUSTER_MANAGER_API_OFFLINE_TOKEN"
'''

RETURN = r'''
original_message:
    description: The original params that were passed in to be deleted.
    type: dict 
    returned: always in case of success
message:
    description: The output error / exception message that is returned in the case the module generates an error / exception.
    type: dict
    returned: in case of error / exception
env_url_error:
    description: The error message returned if no environment variable is passed for the BASE_HOST URL.
    type: str
    returned: If the module uses default url instead of passed environment variable.
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_service_accounts_mgmt_sdk
import auth.rhoas_auth as auth
from rhoas_service_accounts_mgmt_sdk.api import service_accounts_api

load_dotenv(".env")

def run_module():
    module_args = dict(
        service_account_id=dict(type='str', required=True),
        openshift_offline_token=dict(type='str', required=False),
    )
    
    result = dict(
        changed=False,
        original_message='',
        message='',
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
    
    configuration = rhoas_service_accounts_mgmt_sdk.Configuration()
    sso_base_host = os.getenv("SSO_BASE_HOST") 
    if sso_base_host is None:
        result['env_url_error'] = 'cannot find SSO_BASE_HOST in .env file, using default url values instead'
        sso_base_host = SSO_BASE_HOST
    configuration = rhoas_service_accounts_mgmt_sdk.Configuration(
        host = sso_base_host,
    )
    configuration.access_token = token["access_token"]

    with rhoas_service_accounts_mgmt_sdk.ApiClient(configuration) as api_client:
        api_instance = service_accounts_api.ServiceAccountsApi(api_client)
        try:
            service_account_id = module.params['service_account_id']
            result['original_message'] = f'Deleting Service Account with ID: {service_account_id}'
            api_instance.delete_service_account(service_account_id)
            result['changed'] = True
            module.exit_json(**result)
        except rhoas_service_accounts_mgmt_sdk.ApiException as e:
            rb = json.loads(e.body)
            result['message'] = e.body
            module.fail_json(msg=f'Failed to delete service account with ID: `{service_account_id}`. Error: `{rb["error"]}`. Reason for failure: `{rb["error_description"]}`.')
        except Exception as e:
            result['message'] = e
            module.fail_json(msg='Failed to delete service account.')

def main():
    run_module()


if __name__ == '__main__':
    main()