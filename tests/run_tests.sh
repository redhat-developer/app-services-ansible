#!/bin/bash

source env/bin/activate

set -u
trap 'echo "[ERROR] Unbound variable must be set"' EXIT

TESTING_ENVIRONMENT=${1:-"stage"}
JUNIT_XML_REPORT=${2:-"junit_report.xml"}
LOGFILE=${3:-"pytest.log"}

# init env vars
if [ "${TESTING_ENVIRONMENT}" == "prod" ]; then
    API_BASE_HOST="https://api.openshift.com"
    SSO_BASE_HOST="https://sso.redhat.com/auth/realms/redhat-external"
elif [ "${TESTING_ENVIRONMENT}" == "stage" ]; then
    API_BASE_HOST="https://api.stage.openshift.com"
    SSO_BASE_HOST="https://sso.stage.redhat.com/auth/realms/redhat-external"
else
    echo "[ERROR] \$TESTING_ENVIRONMENT is set to '$TESTING_ENVIRONMENT'. Only possible values are 'prod' and 'stage'"
    exit 1
fi

export API_BASE_HOST
export SSO_BASE_HOST
export OFFLINE_TOKEN="${OFFLINE_TOKEN}"

# run test suite
pytest test_suite/get_kafkas.py --junit-xml=${JUNIT_XML_REPORT} --log-file=${LOGFILE}

trap - EXIT
set +u

deactivate
