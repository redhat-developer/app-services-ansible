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
module: update_kafka_topic

short_description: Update a topic's configuration settings on a Red Hat OpenShift Streams for Apache Kafka Instance.

version_added: "0.1.0-alpha"

description: Update a topic's configuration settings on a Red Hat OpenShift Streams for Apache Kafka Instance.

options:
    topic_name:
        description: Name of the Kafka instance.
        required: true
        type: str
    kafka_id:
        description: ID of the Kafka instance.
        required: true
        type: str
    kafka_admin_url: 
        description: Admin URL of the Kafka instance.
        required: false
        type: str
    partitions:
        description: Number of partitions for the topic.
        required: false
        type: int
    retention_size_bytes:
        description: Retention size in bytes for the topic.
        required: false
        type: str
    retention_period_ms:
        description: Retention period in milliseconds for the topic.
        required: false
        type: str
    cleanup_policy:
        description: Cleanup policy for the topic.
        required: false
        type: str
    openshift_offline_token:
        description: `openshift_offline_token` is the OpenShift Offline Token that is used for authentication to enable communication with the Kafka Management API. If not provided, the `OFFLINE_TOKEN` environment variable will be used.
        required: false
        type: str
 
extends_documentation_fragment:
    - rhoas.rhoas.rhoas_doc_fragment
    
author:
    - Red Hat Developer
'''

EXAMPLES = r'''
# Pass in a message
  - name: Update Kafka Topic
    update_kafka_topic:
      topic_name: "kafka-topic-name"
      kafka_id: "{{ kafka_req_resp.id }}"
      partitions: 1
      retention_period_ms: "86400000"
      retention_size_bytes: "1073741824"
      cleanup_policy: "compact"
      openshift_offline_token: "OPENSHIFT_OFFLINE_TOKEN"
    register:
      update_topic_res_obj

 
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original params that were passed in.
    type: dict 
    returned: always in case of successful execution
message:
    description: A message detailing topic updated successfully.
    type: str
    returned: always in case of successful execution
    sample: "Topic updated successfully"
update_topic_res_obj:
    description: The configuration of the topic that was updated 
    type: dict
    returned: always upon successful update of a topic
kafka_admin_resp_obj:
    description: The response object from the Kafka Admin REST API which details the Kafka instance
    type: dict
    returned: if no Kafka Admin URL is provided in the module parameters and the Kafka Admin URL is retrieved from the Kafka Admin REST API
kafka_admin_url:
    description: The Kafka Admin URL of the Kafka instance
    type: str
    returned: if no Kafka Admin URL is provided in the module parameters and the Kafka Admin URL is retrieved from the Kafka Admin REST API
env_url_error:
    description: The error message returned if no environment variable is passed for the BASE_HOST URL.
    type: str
    returned: If the module uses default url instead of passed environment variable.
'''

load_dotenv(".env")

from ansible.module_utils.basic import AnsibleModule
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import topics_api
from rhoas_kafka_instance_sdk.model.topic_settings import TopicSettings
from rhoas_kafka_instance_sdk.model.config_entry import ConfigEntry


def run_module():
    module_args = dict(
        topic_name=dict(type='str', required=True),
        kafka_id=dict(type='str', required=True),
        kafka_admin_url=dict(type='str', required=False),
        partitions=dict(type='int', required=False),
        retention_size_bytes=dict(type='str', required=False),
        retention_period_ms=dict(type='str', required=False),
        cleanup_policy=dict(type='str', required=False),
        openshift_offline_token=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        original_message=dict,
        message='',
        update_topic_res_obj=dict,
        kafka_admin_resp_obj=dict,
        kafka_admin_url='',
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
    if "http://localhost" in os.environ.get("API_BASE_HOST"):
        token['access_token'] = "DUMMY_TOKEN_FOR_MOCK"
    else:
        token['access_token'] = get_offline_token(module.params['openshift_offline_token'])
        
    api_base_host = os.getenv("API_BASE_HOST") 
    if api_base_host is None:
        result['env_url_error'] = 'cannot find API_BASE_HOST in .env file, using default url values instead'
        api_base_host = API_BASE_HOST
    kafka_mgmt_config = rhoas_kafka_mgmt_sdk.Configuration(
        host = api_base_host,
    )
 
    kafka_mgmt_config.access_token = token["access_token"]
    
    def get_kafka_mgmt_client():
        with rhoas_kafka_mgmt_sdk.ApiClient(kafka_mgmt_config) as kafka_mgmt_api_client:
            # Update an instance of the API class
            kafka_mgmt_api_instance = default_api.DefaultApi(kafka_mgmt_api_client)
            return kafka_mgmt_api_instance
        
    def get_kafka_admin_url(kafka_mgmt_api_instance):
        # Check for kafka_admin_url to be used to update topic
        while (result['kafka_admin_url'] == ""):
            # Enter a context with an instance of the API client
                kafka_id = module.params['kafka_id'] 

                try:
                    kafka_mgmt_api_response = kafka_mgmt_api_instance.get_kafka_by_id(kafka_id)
                    result['kafka_admin_url'] = kafka_mgmt_api_response['admin_api_server_url']
                    result['kafka_admin_resp_obj'] = kafka_mgmt_api_response.to_dict()
                except rhoas_kafka_mgmt_sdk.ApiException as e:
                    rb = json.loads(e.body)
                    module.fail_json(msg=f'Failed to get kafka admin URL with API exception code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.')
                except Exception as e:
                    module.fail_json(msg=f'Failed to get kafka admin URL with general exception: `{e}`.')
                
    # Check for kafka_admin_url to be used to update topic
    if (module.params['kafka_admin_url'] is None) or (module.params['kafka_admin_url'] == ""):
        get_kafka_admin_url(get_kafka_mgmt_client())

    configuration = rhoas_kafka_instance_sdk.Configuration()
    configuration.host = result['kafka_admin_url']
    configuration.access_token = token["access_token"]
    
    with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
        api_instance = topics_api.TopicsApi(api_client)
        
        number_of_partitions = 1 
        config_entry_dict = {}
        
        #check for user input variables 
        if module.params['retention_size_bytes'] is not None:
            retention_size_bytes=module.params['retention_size_bytes']
            config_entry_dict = { "retention.bytes": retention_size_bytes}
            
        if module.params['retention_period_ms'] is not None:
            retention_period_ms=module.params['retention_period_ms']
            config_entry_dict = { "retention.ms": retention_period_ms}
            
        if module.params['cleanup_policy'] is not None:
            cleanup_policy=module.params['cleanup_policy']
            config_entry_dict = { "cleanup.policy": cleanup_policy}
            
        if module.params['partitions'] is not None:
            number_of_partitions=module.params['partitions']
          
        config = [ConfigEntry(key=key, value=value) for key, value in config_entry_dict.items()]
        topic_name=module.params['topic_name']
        topic_settings=TopicSettings(
            num_partitions=number_of_partitions,
            config=config
        )
        try:
            api_response = api_instance.update_topic(topic_name, topic_settings, async_req=True)
            result['update_topic_res_obj'] = api_response.get().to_dict()
            result['changed'] = True
            result['original_message'] = topic_settings.to_dict()
            result['message'] = "Topic updated successfully"
            module.exit_json(**result)
        except rhoas_kafka_instance_sdk.ApiException as e:
            print("Exception when calling TopicsApi->update_topic: %s \ n" % e)
            rb = json.loads(e.body)
            module.fail_json(msg=f'Failed to update kafka topic with API error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}` because `{rb["detail"]}`)', **result)
        except Exception as e:
            module.fail_json(msg=f'Failed to update kafka topic with general error: `{e}`', **result)

def main():
    run_module()


if __name__ == '__main__':
    main()
