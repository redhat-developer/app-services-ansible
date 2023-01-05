import logging, json
import test_utils

LOGGER = logging.getLogger(__name__)

module = 'get_kafkas'

class TestGetKafkas:
    def test_no_kafkas_available(self):
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
