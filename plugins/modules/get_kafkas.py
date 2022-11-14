#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from __future__ import absolute_import, division, print_function
import json
import os

from dotenv import load_dotenv

from ..module_utils.common import get_offline_token
from ..module_utils.constants.constants import API_BASE_HOST

DOCUMENTATION = r'''
---
module: get_kafkas

short_description: Retrieves a list of all Red Hat OpenShift Streams for Apache Kafka Instances available in the users organization.

version_added: "0.1.1"

description: Retrieves a list of all Red Hat OpenShift Streams for Apache Kafka Instances available in the users organization.

options:
    page:
        description: Page index number.
        required: false
        type: string
    size:
        description: Page size.
        required: false
        type: string
    order_by:
        description: Order by.
        required: false
        type: string
    search:
        description: Search query.
        required: false
        type: string
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
  - name: Get kafkas
    rhoas.rhoas.get_kafkas:
        page: '1'
        size: '100'
        order_by: 'name asc'
        openshift_offline_token: "OPENSHIFT_OFFLINE_TOKEN"
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
env_url_error:
    description: The error message returned if no environment variable is passed for the BASE_HOST URL.
    type: str
    returned: If the module uses default url instead of passed environment variable.
'''

import rhoas_kafka_mgmt_sdk
from ansible.module_utils.basic import AnsibleModule
from rhoas_kafka_mgmt_sdk.api import default_api

load_dotenv(".env")

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        openshift_offline_token=dict(type='str', required=False),
        page = dict(type='str', required=False),
        size = dict(type='str', required=False),
        order_by = dict(type='str', required=False),
        search = dict(type='str', required=False),

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
    configuration = rhoas_kafka_mgmt_sdk.Configuration(
        host = api_base_host,
    )

    configuration.access_token = token["access_token"]
    # Enter a context with an instance of the API client
    with rhoas_kafka_mgmt_sdk.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = default_api.DefaultApi(api_client)
        _async = True # bool | Perform the action in an asynchronous manner

        if module.params['page'] is not None:
            page = module.params['page']
        else:
            page = '1' # str | Page index (optional)

        if module.params['size'] is not None:
            size = module.params['size']
        else:
            size = '100'

        if module.params['order_by'] is not None:
            order_by = module.params['order_by']
        else:
            order_by = "name asc" # str | Specifies the order by criteria. The syntax of this parameter is similar to the syntax of the `order by` clause of an SQL statement. Each query can be ordered by any of the following `kafkaRequests` fields:  * bootstrap_server_host * admin_api_server_url * cloud_provider * cluster_id * created_at * href * id * instance_type * multi_az * name * organisation_id * owner * reauthentication_enabled * region * status * updated_at * version  For example, to return all Kafka instances ordered by their name, use the following syntax:  ```sql name asc ```  To return all Kafka instances ordered by their name _and_ created date, use the following syntax:  ```sql name asc, created_at asc ```  If the parameter isn't provided, or if the value is empty, then the results are ordered by name. (optional)

        if module.params['search'] is not None:
            search = module.params['search']
        else:
            search = "" # str | Search criteria.  The syntax of this parameter is similar to the syntax of the `where` clause of an SQL statement. Allowed fields in the search are `cloud_provider`, `name`, `owner`, `region`, and `status`. Allowed comparators are `<>`, `=`, `LIKE`, or `ILIKE`. Allowed joins are `AND` and `OR`. However, you can use a maximum of 10 joins in a search query.  Examples:  To return a Kafka instance with the name `my-kafka` and the region `aws`, use the following syntax:  ``` name = my-kafka and cloud_provider = aws ```[p-]  To return a Kafka instance with a name that starts with `my`, use the following syntax:  ``` name like my%25 ```  To return a Kafka instance with a name containing `test` matching any character case combinations, use the following syntax:  ``` name ilike %25test%25 ```  If the parameter isn't provided, or if the value is empty, then all the Kafka instances that the user has permission to see are returned.  Note. If the query is invalid, an error is returned.  (optional)
        try:
            api_response = api_instance.get_kafkas(async_req=True, page=page, size=size, order_by=order_by, search=search)
            kafka_req_resp = api_response.get(20000).to_dict()
            result['message'] = kafka_req_resp

            # exit the module and return the state
            module.exit_json(**result)
        except rhoas_kafka_mgmt_sdk.ApiException as e:
            rb = json.loads(e.body)
            module.fail_json(msg=f'Failed to get new kafka instance with error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.')
        except Exception as e:
            module.fail_json(msg=f'Failed to get new kafka instance with error: `{e}`.')

def main():
    run_module()


if __name__ == '__main__':
    main()
