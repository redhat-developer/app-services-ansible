#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from __future__ import (absolute_import, division, print_function)
import json

from ..module_utils.constants.constants import API_BASE_HOST

DOCUMENTATION = r'''
---
module: create_kafka_topic

short_description: Create a topic on a Red Hat OpenShift Streams for Apache Kafka Instance

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.1.1-aplha"

description: Create a topic on a Red Hat OpenShift Streams for Apache Kafka Instance

options:
    name:
        description: Name of the Kafka instance
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
    partitions:
        description: Number of partitions for the topic
        required: false
        type: int
    retention_size_bytes:
        description: Retention size in bytes for the topic
        required: false
        type: str
    retention_period_ms:
        description: Retention period in milliseconds for the topic
        required: false
        type: str
    cleanup_policy:
        description: Cleanup policy for the topic
        required: false
        type: str
 
extends_documentation_fragment:
    - dimakis.rhosak_test.rhosak_doc_fragment
    
author:
    - Red Hat Developer
'''

EXAMPLES = r'''
# Pass in a message
  - name: Create Kafka Topic
    create_kafka_topic:
      name: "kafka-topic-name"
      kafka_id: "{{ kafka_req_resp.id }}"
      partitions: 1
      retention_period_ms: "86400000"
      retention_size_bytes: "1073741824"
      cleanup_policy: "compact"
    register:
      create_topic_res_obj

 
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original params that were passed in.
    type: dict 
    returned: always in case of successful execution
message:
    description: A message detailing topic created successfully.
    type: str
    returned: always in case of successful execution
    sample: "Topic created successfully"
create_topic_res_obj:
    description: The configuration of the topic that was created 
    type: dict
    returned: always upon successful creation of a topic
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
from rhoas_kafka_instance_sdk.api import topics_api
from rhoas_kafka_instance_sdk.model.new_topic_input import NewTopicInput
from rhoas_kafka_instance_sdk.model.topic_settings import TopicSettings
from rhoas_kafka_instance_sdk.model.config_entry import ConfigEntry

configuration = rhoas_kafka_instance_sdk.Configuration(
    host = API_BASE_HOST
)

token = auth.get_access_token()

def run_module():
    module_args = dict(
        name=dict(type='str', required=True),
        kafka_id=dict(type='str', required=True),
        kafka_admin_url=dict(type='str', required=False),
        partitions=dict(type='int', required=False),
        retention_size_bytes=dict(type='str', required=False),
        retention_period_ms=dict(type='str', required=False),
        cleanup_policy=dict(type='str', required=False),
    )

    result = dict(
        changed=False,
        original_message=dict,
        message='',
        create_topic_res_obj=dict,
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
            # Create an instance of the API class
            kafka_mgmt_api_instance = default_api.DefaultApi(kafka_mgmt_api_client)
            return kafka_mgmt_api_instance
        
    def get_kafka_admin_url(kafka_mgmt_api_instance):
        # Check for kafka_admin_url to be used to create topic
        while (result['kafka_admin_url'] == ""):
            # Enter a context with an instance of the API client
                kafka_id = module.params['kafka_id'] 

                try:
                    kafka_mgmt_api_response = kafka_mgmt_api_instance.get_kafka_by_id(kafka_id)
                    kafka_mgmt_api_response
                    result['kafka_admin_url'] = kafka_mgmt_api_response['admin_api_server_url']
                    result['kafka_admin_resp_obj'] = kafka_mgmt_api_response.to_dict()
                    
                except rhoas_kafka_mgmt_sdk.ApiException as e:
                    rb = json.loads(e.body)
                    module.fail_json(msg=f'Failed to create kafka topic with API exception code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}`.')
                except Exception as e:
                    module.fail_json(msg=f'Failed to create kafka topic with general exception: `{e}`.')
                
    # Check for kafka_admin_url to be used to create topic
    if (module.params['kafka_admin_url'] is None) or (module.params['kafka_admin_url'] == ""):
        get_kafka_admin_url(get_kafka_mgmt_client())

    configuration.host = result['kafka_admin_url']
    configuration.access_token = token["access_token"]
    
    with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
        api_instance = topics_api.TopicsApi(api_client)
        
        number_of_partitions = 1 
        config_entry_flag = False
        config_entry_dict = {}
        
        #check for user input variables 
        if module.params['retention_size_bytes'] is not None:
            retention_size_bytes=module.params['retention_size_bytes']
            config_entry_dict = { "retention.bytes": retention_size_bytes}
            config_entry_flag = True
            
        if module.params['retention_period_ms'] is not None:
            retention_period_ms=module.params['retention_period_ms']
            config_entry_dict = { "retention.ms": retention_period_ms}
            config_entry_flag = True
            
        if module.params['cleanup_policy'] is not None:
            cleanup_policy=module.params['cleanup_policy']
            config_entry_dict = { "cleanup.policy": cleanup_policy}
            config_entry_flag = True
            
        if module.params['partitions'] is not None:
            number_of_partitions=module.params['partitions']
            config_entry_flag = True
          
        # create a standard topic with presets stemming from the API 
        if not config_entry_flag:
            new_topic_input = NewTopicInput(
                name=module.params['name'],
                settings=TopicSettings(
                    num_partitions=number_of_partitions,
                )
            )
        else:
            # create a topic with custom settings as passed in by the user 
            config = [ConfigEntry(key=key, value=value) for key, value in config_entry_dict.items()]
            new_topic_input = NewTopicInput(
                name=module.params['name'],
                settings=TopicSettings(
                    num_partitions=number_of_partitions,
                    config=config
                    )
            )
        try:
            api_response = api_instance.create_topic(new_topic_input)
            result['create_topic_res_obj'] = api_response.to_dict()
            result['changed'] = True
            result['original_message'] = new_topic_input.to_dict()
            result['message'] = "Topic created successfully"
            module.exit_json(**result)
        except rhoas_kafka_instance_sdk.ApiException as e:
            print("Exception when calling TopicsApi->create_topic: %s \ n" % e)
            rb = json.loads(e.body)
            module.fail_json(msg=f'Failed to create kafka topic with error code: `{rb["code"]}`. The reason of failure: `{rb["reason"]}` because `{rb["detail"]}`)', **result)
        except Exception as e:
            module.fail_json(msg=f'Failed to create kafka topic with error: `{e}`', **result)

def main():
    run_module()


if __name__ == '__main__':
    main()
