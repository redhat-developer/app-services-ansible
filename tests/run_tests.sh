#!/bin/bash

TESTS_PATH="${TESTS_PATH:-"$(cd -- "$(dirname "${BASH_SOURCE[0]}")" > /dev/null 2>&1 && pwd)"}"
REPO_ROOT="$TESTS_PATH/../"

source $TESTS_PATH/venv/bin/activate

set -u
trap 'echo "[ERROR] Unbound variable must be set"' EXIT

# set env vars
export TESTING_ENVIRONMENT=${TESTING_ENVIRONMENT:-"stage"}
if [ "${TESTING_ENVIRONMENT}" == "prod" ]; then
    export API_BASE_HOST="https://api.openshift.com"
elif [ "${TESTING_ENVIRONMENT}" == "stage" ]; then
    export API_BASE_HOST="https://api.stage.openshift.com"
else
    echo "[ERROR] \$TESTING_ENVIRONMENT is set to '$TESTING_ENVIRONMENT'. Only possible values are 'prod' and 'stage'"
    exit 1
fi

export OFFLINE_TOKEN=${OFFLINE_TOKEN}
export ANSIBLE_CONFIG="$TESTS_PATH/ansible.cfg"
export SSO_BASE_HOST="https://sso.redhat.com/auth/realms/redhat-external"

export KAFKA_NAME=${KAFKA_NAME:-"kafka-inst-$(openssl rand -hex 4)"}
export BILLING_MODEL=${BILLING_MODEL:-"standard"}
export CLOUD_PROVIDER=${CLOUD_PROVIDER:-"aws"}
export KAFKA_INSTANCE_PLAN=${KAFKA_INSTANCE_PLAN:-"developer.x1"}
export REGION=${REGION:-"us-east-1"}
export TOPIC_NAME=${TOPIC_NAME:-"topic-$(openssl rand -hex 4)"}

export JUNIT_XML_REPORT=${JUNIT_XML_REPORT:-"junit_report.xml"}
export LOGFILE=${LOGFILE:-"pytest.log"}

# run test suite
pytest "$TESTS_PATH/test_suite/basic_test_suite.py" --junit-xml="$TESTS_PATH/${JUNIT_XML_REPORT}" --log-file="$TESTS_PATH/${LOGFILE}"

trap - EXIT
set +u

deactivate
