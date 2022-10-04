#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from __future__ import (absolute_import, division, print_function)
import json

from ..module_utils.constants.constants import API_BASE_HOST
DOCUMENTATION = r'''
---
module: delete_kafka_topic

short_description: Create a topic on a Red Hat OpenShift Streams for Apache Kafka Instance

version_added: "0.1.0"

description: Create a topic on a Red Hat OpenShift Streams for Apache Kafka Instance

options:
    topic_name:
        description: Name of the Kafka instance topic
        required: true
        type: str
    kafka_id:
        description: ID of the Kafka instance
        required: true
        type: str
    kafka_admin_url: 
        description: Admin URL of the Kafka instance
        required: false
        type: str
 
author:
    - Red Hat Developer
'''

EXAMPLES = r'''
# Pass in a message
  - name: Delete Kafka Topic
    delete_kafka_topic:
      name: "KAFKA_TOPIC_NAME"
      kafka_id: "KAFKA_ID"
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original params that were passed in.
    type: dict 
    returned: always in case of successful execution
message:
    description: A message detailing topic to be deleted.
    type: str
    returned: always in case of successful execution
kafka_admin_resp_obj:
    description: The response object from the Kafka Admin REST API which details the Kafka instance
    type: dict
    returned: if no Kafka Admin URL is provided in the module parameters and the Kafka Admin URL is retrieved from the Kafka Admin REST API
kafka_admin_url:
    description: The Kafka Admin URL of the Kafka instance
    type: str
    returned: if no Kafka Admin URL is provided in the module parameters and the Kafka Admin URL is retrieved from the Kafka Admin REST API
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
import auth.rhoas_auth as auth
import rhoas_kafka_instance_sdk
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import topics_api

configuration = rhoas_kafka_instance_sdk.Configuration()

token = auth.get_access_token()

def run_module():
    module_args = dict(
        topic_name=dict(type='str', required=True),
        kafka_id=dict(type='str', required=True),
        kafka_admin_url=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        original_message='',
        message='',
        kafka_admin_resp_obj=dict,
        kafka_admin_url=''
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    if module.check_mode:
        module.exit_json(**result)

    kafka_mgmt_config = rhoas_kafka_mgmt_sdk.Configuration(
        host = API_BASE_HOST,
    )
 
    token = auth.get_access_token()
    kafka_mgmt_config.access_token = token["access_token"]
    
    def get_kafka_mgmt_client():
        with rhoas_kafka_mgmt_sdk.ApiClient(kafka_mgmt_config) as kafka_mgmt_api_client:
            kafka_mgmt_api_instance = default_api.DefaultApi(kafka_mgmt_api_client)
            return kafka_mgmt_api_instance
        
    def get_kafka_admin_url(kafka_mgmt_api_instance):
        # Check for kafka_admin_url to be used to delete topic
        while (result['kafka_admin_url'] == ""):
                kafka_id = module.params['kafka_id'] 

                try:
                    kafka_mgmt_api_response = kafka_mgmt_api_instance.get_kafka_by_id(kafka_id)
                    result['kafka_admin_url'] = kafka_mgmt_api_response['admin_api_server_url']
                    result['kafka_admin_resp_obj'] = kafka_mgmt_api_response.to_dict()
                    configuration.host = result['kafka_admin_url']
                except rhoas_kafka_mgmt_sdk.ApiException as e:
                    rb = json.loads(e.body)
                    module.fail_json(msg=f'Failed to delete kafka topic with error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.')
                except Exception as e:
                    module.fail_json(msg=f'Failed to delete kafka topic with error: `{e}`.')
                
    # Check for kafka_admin_url to be used to delete topic
    if (module.params['kafka_admin_url'] is None) or (module.params['kafka_admin_url'] == ""):
        get_kafka_admin_url(get_kafka_mgmt_client())

    configuration.access_token = token["access_token"]
    
    with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
        api_instance = topics_api.TopicsApi(api_client)
        topic_name = module.params['topic_name'] 
          
        try:
            api_instance.delete_topic(topic_name)
            result['changed'] = True
            result['original_message'] = f'Topic `{topic_name}` deleted successfully.'
            result['message'] = "Topic deleted successfully"
            module.exit_json(**result)
        except rhoas_kafka_instance_sdk.ApiException as e:
            rb = json.loads(e.body)
            result['message'] = f'{e.body}'
            module.fail_json(msg=f'Failed to delete kafka topic with error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}` because `{rb["detail"]}`)', **result)
        except Exception as e:
            result['message'] = f'{e}'
            module.fail_json(msg=f'Failed to delete kafka topic with error: `{e}`.', **result)

def main():
    run_module()


if __name__ == '__main__':
    main()
