#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from __future__ import (absolute_import, division, print_function)
import json

from ..module_utils.constants.constants import SSO_BASE_HOST

DOCUMENTATION = r'''
---
module: delete_service_account_by_id

short_description: Delete a Service Account for use with Red Hat Openshift Application Services 

version_added: "0.1.0"

description: Delete a Service Account for use with Red Hat Openshift Application Services 

options:
    service_account_id:
        description: ID of the Service Account
        required: true
        type: str
 
extends_documentation_fragment:
    - dimakis.rhoask_test.rhosak_doc_fragment

author:
    - Red Hat Developer
'''

EXAMPLES = r'''
  - name: Delete Service Account
    delete_service_account_by_id:
        service_account_id: "SERVICE_ACCOUNT_ID"
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
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_service_accounts_mgmt_sdk
import auth.rhoas_auth as auth
from rhoas_service_accounts_mgmt_sdk.api import service_accounts_api

def run_module():
    module_args = dict(
        service_account_id=dict(type='str', required=True),
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
    
    configuration = rhoas_service_accounts_mgmt_sdk.Configuration(
        host = SSO_BASE_HOST
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
            module.fail_json(msg='Failed to delete service account', **result)

def main():
    run_module()


if __name__ == '__main__':
    main()