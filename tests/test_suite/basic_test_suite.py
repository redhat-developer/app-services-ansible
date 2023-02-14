import logging, json
import pytest
import test_utils
from test_base import wrapper

LOGGER = logging.getLogger(__name__)

class TestBasicTestSuite:

    def test_no_kafkas_available(self, wrapper):
        module = 'get_kafkas'
        ansible_output = test_utils.run_ansible_rhosak_module(module)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'SUCCESS'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == False
        assert dct['env_url_error'] == ''
        assert dct['message'] is not None
        assert dct['message']['items'] == []
        assert dct['message']['page'] == 1
        assert dct['message']['size'] == 0
        assert dct['message']['total'] == 0
        assert dct['original_message'] == ''

    def test_create_kafka_cluster(self, wrapper):
        module = 'create_kafka'
        params = 'name={} billing_model={} cloud_provider={} plan={} region={}'.format(pytest.KAFKA_NAME, pytest.BILLING_MODEL, pytest.CLOUD_PROVIDER, pytest.KAFKA_INSTANCE_PLAN, pytest.REGION)
        ansible_output = test_utils.run_ansible_rhosak_module(module, params)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'CHANGED'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == True
        assert dct['env_url_error'] == ''
        assert dct['kafka_admin_resp_obj'] is not None
        pytest.KAFKA_ID = dct['kafka_admin_resp_obj']['id']
        pytest.ADMIN_API_SERVER_URL = dct['kafka_admin_resp_obj']['admin_api_server_url']
        self.check_kafka_instance_fields(dct['kafka_admin_resp_obj'])
        assert dct['kafka_admin_url'] is not None
        assert dct['kafka_id'] is not None
        assert dct['kafka_state'] == 'ready'
        assert dct['message'] == ''
        assert dct['original_message'] is not None

    def test_get_kafkas(self, wrapper):
        module = 'get_kafkas'
        ansible_output = test_utils.run_ansible_rhosak_module(module)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'SUCCESS'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == False
        assert dct['env_url_error'] == ''
        assert dct['message'] is not None
        assert dct['message']['page'] == 1
        assert dct['message']['size'] == 1
        assert dct['message']['total'] == 1
        assert dct['original_message'] == ''
        item_id = dct['message']['size'] - 1
        self.check_kafka_instance_fields(dct['message']['items'][item_id])

    def test_create_service_account(self, wrapper):
        module = 'create_service_account'
        params = 'name={} description={}'.format(pytest.KAFKA_NAME + '_svc_acc', pytest.KAFKA_NAME + '_svc_acc_desc')
        ansible_output = test_utils.run_ansible_rhosak_module(module, params)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'CHANGED'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == True
        assert dct['client_id'] is not None
        assert dct['client_secret'] is not None
        assert dct['env_url_error'] == ''
        assert dct['message'] == ''
        assert dct['original_message'] == ''
        assert dct['srvce_acc_resp_obj'] is not None
        assert dct['srvce_acc_resp_obj']['client_id'] is not None
        assert dct['srvce_acc_resp_obj']['client_secret'] is not None
        assert dct['srvce_acc_resp_obj']['client_id'] == dct['client_id']
        assert dct['srvce_acc_resp_obj']['client_secret'] == dct['client_secret']

        pytest.SVC_ACC_ID = dct['srvce_acc_resp_obj']['client_id']

    def test_create_kafka_acl_binding(self, wrapper):
        module = 'create_kafka_acl_binding'
        operation_type = "ALL"
        pattern_type = "PREFIXED"
        permission_type = "ALLOW"
        resource_type = "TOPIC"
        params = 'kafka_id={} principal={} resource_name={} resource_type={} pattern_type={} operation_type={} permission_type={} kafka_admin_url={}'.format(pytest.KAFKA_ID, pytest.SVC_ACC_ID, pytest.TOPIC_NAME, resource_type, pattern_type, operation_type, permission_type, pytest.ADMIN_API_SERVER_URL)
        ansible_output = test_utils.run_ansible_rhosak_module(module, params)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'CHANGED'
    
        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == True
        assert dct['env_url_error'] == ''
        assert dct['kafka_admin_resp_obj'] == ''
        assert dct['kafka_admin_url'] == pytest.ADMIN_API_SERVER_URL
        assert dct['message'] == 'ACL Binding Created'
        assert dct['original_message'] is not None
        assert dct['original_message']['operation'] == operation_type
        assert dct['original_message']['pattern_type'] == pattern_type
        assert dct['original_message']['permission'] == permission_type
        assert dct['original_message']['principal'] == 'User:{}'.format(pytest.SVC_ACC_ID)
        assert dct['original_message']['resource_name'] == pytest.TOPIC_NAME
        assert dct['original_message']['resource_type'] == resource_type

    def test_create_kafka_topic(self, wrapper):
        module = 'create_kafka_topic'
        params = 'kafka_id={} topic_name={}'.format(pytest.KAFKA_ID, pytest.TOPIC_NAME)
        ansible_output = test_utils.run_ansible_rhosak_module(module, params)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'CHANGED'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == True
        assert dct['create_topic_res_obj'] is not None
        assert dct['kafka_admin_resp_obj'] is not None
        assert dct['kafka_admin_url'] == pytest.ADMIN_API_SERVER_URL
        assert dct['message'] == 'Topic created successfully'
        assert dct['original_message'] is not None
        assert dct['original_message']['name'] == pytest.TOPIC_NAME
        assert dct['original_message']['settings'] == {}

        self.check_topic_fields(dct['create_topic_res_obj'])
        self.check_kafka_instance_fields(dct['kafka_admin_resp_obj'])

    def test_delete_kafka_topic(self, wrapper):
        module = 'delete_kafka_topic'
        params = 'kafka_id={} topic_name={}'.format(pytest.KAFKA_ID, pytest.TOPIC_NAME)
        ansible_output = test_utils.run_ansible_rhosak_module(module, params)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'CHANGED'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == True
        assert dct['env_var'] == ''
        assert dct['kafka_admin_resp_obj'] is not None
        assert dct['kafka_admin_url'] == pytest.ADMIN_API_SERVER_URL
        assert dct['message'] == 'Topic deleted successfully'
        assert dct['original_message'] == 'Topic `{}` deleted successfully.'.format(pytest.TOPIC_NAME)

        self.check_kafka_instance_fields(dct['kafka_admin_resp_obj'])

    def test_delete_service_account(self, wrapper):
        module = 'delete_service_account_by_id'
        params = 'service_account_id={}'.format(pytest.SVC_ACC_ID)
        ansible_output = test_utils.run_ansible_rhosak_module(module, params)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'CHANGED'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == True
        assert dct['env_url_error'] == ''
        assert dct['message'] == ''
        assert dct['original_message'] == 'Deleting Service Account with ID: {}'.format(pytest.SVC_ACC_ID)

    def test_delete_kafka_by_id(self, wrapper):
        module = 'delete_kafka_by_id'
        params = 'kafka_id={}'.format(pytest.KAFKA_ID)
        ansible_output = test_utils.run_ansible_rhosak_module(module, params)
        ansible_output_status = test_utils.get_ansible_response_status(ansible_output)
        assert ansible_output_status == 'CHANGED'

        response_json = test_utils.format_ansible_response_to_json(ansible_output)
        dct = json.loads(response_json)
        assert dct['changed'] == True
        assert dct['env_var_error'] == ''
        assert dct['message'] == 'Kafka instance deleted'
        assert dct['original_message'] == 'Kafka instance with ID: {} set for deletion'.format(pytest.KAFKA_ID)
    
    def check_kafka_instance_fields(self, kafka_obj):
        assert kafka_obj['admin_api_server_url'] is not None
        assert kafka_obj['billing_model'] is not None
        assert kafka_obj['bootstrap_server_host'] is not None
        assert kafka_obj['browser_url'] is not None
        assert kafka_obj['cloud_provider'] is not None
        assert kafka_obj['created_at'] is not None
        assert kafka_obj['egress_throughput_per_sec'] is not None
        assert kafka_obj['expires_at'] is not None
        assert kafka_obj['href'] is not None
        assert kafka_obj['id'] is not None
        assert kafka_obj['ingress_throughput_per_sec'] is not None
        assert kafka_obj['instance_type'] is not None
        assert kafka_obj['instance_type_name'] is not None
        assert kafka_obj['kafka_storage_size'] is not None
        assert kafka_obj['kind'] is not None
        assert kafka_obj['max_connection_attempts_per_sec'] is not None
        assert kafka_obj['max_data_retention_period'] is not None
        assert kafka_obj['max_data_retention_size'] is not None
        assert kafka_obj['max_partitions'] is not None
        assert kafka_obj['multi_az'] is not None
        assert kafka_obj['name'] is not None
        assert kafka_obj['owner'] is not None
        assert kafka_obj['reauthentication_enabled'] is not None
        assert kafka_obj['region'] is not None
        assert kafka_obj['size_id'] is not None
        assert kafka_obj['status'] is not None
        assert kafka_obj['total_max_connections'] is not None
        assert kafka_obj['updated_at'] is not None
        assert kafka_obj['version'] is not None

        assert kafka_obj['status'] == 'ready'
        assert kafka_obj['billing_model'] == pytest.BILLING_MODEL
        assert kafka_obj['cloud_provider'] == pytest.CLOUD_PROVIDER
        assert kafka_obj['instance_type'] == pytest.KAFKA_INSTANCE_PLAN.split('.')[0]
        assert kafka_obj['size_id'] == pytest.KAFKA_INSTANCE_PLAN.split('.')[1]
        assert kafka_obj['instance_type_name'] == 'Trial'
        assert kafka_obj['name'] == pytest.KAFKA_NAME
        assert kafka_obj['region'] == pytest.REGION
        assert kafka_obj['id'] == pytest.KAFKA_ID
        assert kafka_obj['admin_api_server_url'] == pytest.ADMIN_API_SERVER_URL

    def check_topic_fields(self, topic_obj):
        assert topic_obj['config'] is not None
        assert topic_obj['href'] == '/api/v1/topics/{}'.format(pytest.TOPIC_NAME)
        assert topic_obj['id'] == pytest.TOPIC_NAME
        assert topic_obj['is_internal'] == False
        assert topic_obj['kind'] =='Topic'
        assert topic_obj['name'] == pytest.TOPIC_NAME
        assert topic_obj['partitions'] is not None
        