#!/bin/bash

source venv/bin/activate

set -u
trap 'echo "[ERROR] Unbound variable must be set"' EXIT

TESTING_ENVIRONMENT=${1:-"stage"}
JUNIT_XML_REPORT=${2:-"junit_report.xml"}
LOGFILE=${3:-"pytest.log"}

# init env vars
if [ "${TESTING_ENVIRONMENT}" == "prod" ]; then
    export API_BASE_HOST="https://api.openshift.com"
elif [ "${TESTING_ENVIRONMENT}" == "stage" ]; then
    export API_BASE_HOST="https://api.stage.openshift.com"
else
    echo "[ERROR] \$TESTING_ENVIRONMENT is set to '$TESTING_ENVIRONMENT'. Only possible values are 'prod' and 'stage'"
    exit 1
export SSO_BASE_HOST="https://sso.redhat.com/auth/realms/redhat-external"
export OFFLINE_TOKEN="${OFFLINE_TOKEN}"
fi

# init test config vars
export KAFKA_NAME=${KAFKA_NAME:-"unique-kafka-name"}
export BILLING_MODEL=${BILLING_MODEL:-"standard"}
export CLOUD_PROVIDER=${CLOUD_PROVIDER:-"aws"}
export KAFKA_INSTANCE_PLAN=${KAFKA_INSTANCE_PLAN:-"developer.x1"}
export REGION=${REGION:-"us-east-1"}
export TOPIC_NAME=${TOPIC_NAME:-"topic-$(openssl rand -hex 4)"}

# run test suite
pytest test_suite/basic_test_suite.py --junit-xml=${JUNIT_XML_REPORT} --log-file=${LOGFILE}

trap - EXIT
set +u

deactivate
