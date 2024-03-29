import subprocess, logging, re
import shlex

LOGGER = logging.getLogger(__name__)

def get_ansible_response_status(ansible_response):
    return re.search(r' \| (.*) => ', ansible_response).group(1)

def format_ansible_response_to_json(ansible_response):
    json = ansible_response
    json = json.replace('localhost | SUCCESS => ', '')
    json = json.replace('localhost | CHANGED => ', '')
    json = json.replace('localhost | FAILED => ', '')
    return json

def run_ansible_command(command):
    process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    output, error = process.communicate()
    output = output.decode('utf-8')
    LOGGER.debug(output)
    if error:
        error=error.decode('utf-8')
        LOGGER.error(error)
        assert error is None
    return output

def run_ansible_rhosak_module(module, params=''):
    command = 'ansible localhost -m rhoas.rhoas.{}'.format(module)
    if params:
        command += ' -a \'{}\''.format(params)
    LOGGER.info(command)
    return run_ansible_command(command)
