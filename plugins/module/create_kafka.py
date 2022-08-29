#!/usr/bin/python


from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: create_kafka

short_description: Create Red Hat OpenShift Streams for Apache Kafka Instance

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "0.1.0"

description: Create Red Hat OpenShift Streams for Apache Kafka Instance

options:
    name:
        description: Name of the Kafka instance
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
- name: Test with a message
  my_namespace.my_collection.create_kafka:
    name: my-kafka

 
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule
import rhoas_kafka_mgmt_sdk
from rhoas_kafka_mgmt_sdk.api import default_api
from rhoas_kafka_mgmt_sdk.model.cloud_provider_list import CloudProviderList
from rhoas_kafka_mgmt_sdk.model.cloud_region_list import CloudRegionList
from rhoas_kafka_mgmt_sdk.model.error import Error
from rhoas_kafka_mgmt_sdk.model.kafka_request import KafkaRequest
from rhoas_kafka_mgmt_sdk.model.kafka_request_list import KafkaRequestList
from rhoas_kafka_mgmt_sdk.model.kafka_request_payload import KafkaRequestPayload
from rhoas_kafka_mgmt_sdk.model.kafka_update_request import KafkaUpdateRequest
from rhoas_kafka_mgmt_sdk.model.metrics_instant_query_list import MetricsInstantQueryList
from rhoas_kafka_mgmt_sdk.model.metrics_range_query_list import MetricsRangeQueryList
from rhoas_kafka_mgmt_sdk.model.supported_kafka_instance_types_list import SupportedKafkaInstanceTypesList
from rhoas_kafka_mgmt_sdk.model.version_metadata import VersionMetadata
import util.auth 

configuration = rhoas_kafka_mgmt_sdk.Configuration(
    host = "https://api.openshift.com"
)

def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        name=dict(type='str', required=True),
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # changed is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        original_message='',
        message=''
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
    if module.check_mode:
        module.exit_json(**result)

 
 
    token = util.auth.get_access_token()
    configuration = rhoas_kafka_mgmt_sdk.Configuration(
        access_token = token["access_token"]
    )
    # Enter a context with an instance of the API client
    with rhoas_kafka_mgmt_sdk.ApiClient(configuration) as api_client:
        # Create an instance of the API class
        api_instance = default_api.DefaultApi(api_client)
        _async = True # bool | Perform the action in an asynchronous manner
        kafka_request_payload = KafkaRequestPayload(
            cloud_provider="cloud_provider_example",
            name="name_example",
            region="region_example",
            reauthentication_enabled=True,
            plan="plan_example",
            billing_cloud_account_id="billing_cloud_account_id_example",
            marketplace="marketplace_example",
            billing_model="billing_model_example",
        ) # KafkaRequestPayload | Kafka data
        try:
            api_response = api_instance.create_kafka(_async, kafka_request_payload)
            # manipulate or modify the state as needed (this is going to be the
            result['object'] = api_response
            # use whatever logic you need to determine whether or not this module
            # made any modifications to your target
            result['changed'] = True

            # in the event of a successful module execution, you will want to
            # simple AnsibleModule.exit_json(), passing the key/value results
            module.exit_json(**result)
        except rhoas_kafka_mgmt_sdk.ApiException as e:
            print("Exception when calling DefaultApi->create_kafka: %s\n" % e)

   


def main():
    run_module()


if __name__ == '__main__':
    main()
