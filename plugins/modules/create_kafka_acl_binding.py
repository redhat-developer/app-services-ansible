#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from __future__ import (absolute_import, division, print_function)
import json
import os

from ..module_utils.common import get_offline_token
from ..module_utils.constants.constants import API_BASE_HOST
from dotenv import load_dotenv

DOCUMENTATION = r'''
---
module: create_kafka_acl_binding

short_description: Create Access Control Lists (ACLs) for Red Hat OpenShift Streams for Apache Kafka Instance.

version_added: 0.1.1

description: Create Access Control Lists (ACLs) for Red Hat OpenShift Streams for Apache Kafka Instance.

options:
    principal:
        description: ID of the User or Service Account to bind created ACLs to.
        required: true
        type: str
    kafka_id:
        description: ID of the Kafka instance.
        required: false
        type: str
    kafka_admin_url:
        description: Kafka Admin URL. This is the URL of the Kafka instance to connect to.
        required: false
        type: str
    resource_type:
        description: Resource type of ACL.
        required: true
        type: str
    resource_name:
        description: Resource name of topic for the ACL.
        required: true
        type: str
    pattern_type:
        description: Pattern type of ACL.
        required: true
        type: str
    operation_type:
        description: Operation type of ACL.
        required: true
        type: str
    permission_type:
        description: Permission type of ACL.
        required: true
        type: str
    openshift_offline_token:
        description: openshift_offline_token is the OpenShift Offline Token that is used for authentication to enable communication with the Kafka Management API. If not provided, the OFFLINE_TOKEN environment variable will be used.
        required: false
        type: str

extends_documentation_fragment:
    - rhoas.rhoas.rhoas_doc_fragment

author:
    - Red Hat Developer
    
'''

EXAMPLES = r'''
# Pass in a message
  - name: Create kafka ACL Service Binding
    rhoas.rhoas.create_kafka_acl_binding:
      kafka_id: "{{ kafka_req_resp.kafka_id }}"
      principal: " {{ srvce_acc_resp_obj['client_id'] }}"
      resource_name: "topic_name"
      resource_type: "Topic"
      pattern_type: "PREFIXED"
      operation_type: "all"
      permission_type: "allow"
      openshift_offline_token: "OPENSHIFT_OFFLINE_TOKEN"
    register: kafka_acl_resp
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
message:
    description: ACL Binding Created.
    type: dict
    returned: in success case
kafka_req_resp:
    description: The response object from the Kafka management API.
    type: dict
    returned: If no kafka_admin_url is passed but the Kafka ID is passed, when the module is successful.
kafka_admin_url:
    description: The Kafka Admin URL. This is the URL of the Kafka instance to connect to.
    type: str
    returned: If no kafka_admin_url is passed but the Kafka ID is passed, when the module is successful.
env_url_error:
    description: The error message returned if no environment variable is passed for the BASE_HOST URL.
    type: str
    returned: when the module uses default url instead of passed environment variable
'''

import auth.rhoas_auth as auth
import rhoas_kafka_instance_sdk
import rhoas_kafka_mgmt_sdk
from ansible.module_utils.basic import AnsibleModule
from rhoas_kafka_instance_sdk.api import acls_api
from rhoas_kafka_instance_sdk.model.acl_binding import AclBinding
from rhoas_kafka_instance_sdk.model.acl_operation import AclOperation as aot
from rhoas_kafka_instance_sdk.model.acl_pattern_type import \
    AclPatternType as apt
from rhoas_kafka_instance_sdk.model.acl_permission_type import \
    AclPermissionType as apert
from rhoas_kafka_instance_sdk.model.acl_resource_type import \
    AclResourceType as art
from rhoas_kafka_mgmt_sdk.api import default_api

load_dotenv(".env")

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        kafka_id = dict(type='str', required = False),
        principal = dict(type='str', required = True),
        kafka_admin_url = dict(type='str', required = False),
        resource_type = dict(type='str', required = True),
        resource_name = dict(type='str', required = True),
        pattern_type = dict(type='str', required = True),
        operation_type = dict(type='str', required = True),
        permission_type = dict(type='str', required = True),
        openshift_offline_token=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        kafka_admin_url='',
        kafka_admin_resp_obj='',
        env_url_error='',
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    if module.check_mode:
        result['message'] = 'Check mode is not supported'
        module.exit_json(**result)

    token = {}
    if os.environ.get('API_BASE_HOST') is None:
        os.environ['API_BASE_HOST'] = API_BASE_HOST
    if "http://localhost" in os.environ.get("API_BASE_HOST"):
        token['access_token'] = "DUMMY_TOKEN_FOR_MOCK"
    elif module.params['openshift_offline_token'] is not None:
        token['access_token'] = get_offline_token(module.params['openshift_offline_token'])
    else:
        token['access_token'] = get_offline_token(None)

    api_base_host = os.getenv("API_BASE_HOST")
    if api_base_host is None:
        result['env_url_error'] = 'cannot find API_BASE_HOST in .env file, using default url values instead'
        api_base_host = API_BASE_HOST
    kafka_mgmt_config = rhoas_kafka_mgmt_sdk.Configuration(
        host = api_base_host,
    )

    kafka_mgmt_config.access_token = token["access_token"]

    configuration = rhoas_kafka_instance_sdk.Configuration()

    def get_kafka_mgmt_client():
        with rhoas_kafka_mgmt_sdk.ApiClient(kafka_mgmt_config) as kafka_mgmt_api_client:
            # Create an instance of the API class
            kafka_mgmt_api_instance = default_api.DefaultApi(kafka_mgmt_api_client)
            return kafka_mgmt_api_instance

    def get_kafka_admin_url(kafka_mgmt_api_instance, configuration):
        # Check for kafka_admin_url to be used to create topic
        while (result['kafka_admin_url'] == "") or (result['kafka_admin_url'] == None):
            # Enter a context with an instance of the API client
                kafka_id = module.params['kafka_id']

                try:
                    kafka_mgmt_api_response = kafka_mgmt_api_instance.get_kafka_by_id(kafka_id)
                    kafka_mgmt_api_response
                    result['kafka_admin_url'] = kafka_mgmt_api_response['admin_api_server_url']
                    result['kafka_admin_resp_obj'] = kafka_mgmt_api_response.to_dict()
                except rhoas_kafka_mgmt_sdk.ApiException as e:
                    rb = json.loads(e.body)
                    module.fail_json(msg=f'Failed to create Access Control List binding with API exception code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.', **result)
                except Exception as e:
                    module.fail_json(msg=f'Failed to create Access Control List binding with exception: {e}', **result)

    if (module.params['kafka_admin_url'] is None) or (module.params['kafka_admin_url'] == ""):
        get_kafka_admin_url(get_kafka_mgmt_client())
    else:
        result['kafka_admin_url'] = module.params['kafka_admin_url']

    configuration.host = result['kafka_admin_url']
    configuration.access_token = token["access_token"]
    with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
        api_instance = acls_api.AclsApi(api_client)

        # some light validation as all the params are required to be in all caps
        if module.params['resource_type'] is not None:
            rt = art(module.params['resource_type'].upper())
        if module.params['pattern_type'] is not None:
            pt = apt(module.params['pattern_type'].upper())
        if module.params['operation_type'] is not None:
            op = aot(module.params['operation_type'].upper())
        if module.params['permission_type'] is not None:
            per = apert(module.params['permission_type'].upper())
        if module.params['principal'].startswith('user:') is True:
            prncpl = module.params['principal'].title().replace(" ", "")
            result['message'] = prncpl
        elif module.params['principal'].startswith('User:') is True:
            prncpl = module.params['principal'].replace(" ", "")
            result['message'] = prncpl
        else:
            prncpl = f'User:{module.params["principal"].replace(" ", "")}'

        acl_binding = AclBinding(
            resource_type = rt,
            resource_name = module.params['resource_name'],
            pattern_type =  pt,
            principal = prncpl,
            operation = op,
            permission = per,
        ) # AclBinding | ACL to create
        result['original_message'] = acl_binding.to_dict()
        try:
            api_response = api_instance.create_acl(acl_binding)
            if api_response is None:
                result['message'] = "ACL Binding Created"
                result['changed'] = True

            module.exit_json(**result)
        except rhoas_kafka_instance_sdk.ApiException as e:
            rb = json.loads(e.body)
            module.fail_json(msg=f'Failed to create Access Control List binding with error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.', **result)
        except Exception as e:
            module.fail_json(msg=f'Failed to create Access Control List binding with error: `{e}`.', **result)


def main():
    run_module()


if __name__ == '__main__':
    main()
