import os
import pytest, logging

LOGGER = logging.getLogger(__name__)

# Kafka config global params
pytest.KAFKA_NAME = os.getenv('KAFKA_NAME')
pytest.TOPIC_NAME = os.getenv('TOPIC_NAME')
pytest.BILLING_MODEL = os.getenv('BILLING_MODEL')
pytest.KAFKA_INSTANCE_PLAN = os.getenv('KAFKA_INSTANCE_PLAN')
pytest.CLOUD_PROVIDER = os.getenv('CLOUD_PROVIDER')
pytest.REGION = os.getenv('REGION')
pytest.API_BASE_HOST = os.getenv('API_BASE_HOST')

@pytest.fixture(scope="session")
def wrapper(request):
    LOGGER.info('Input params:')
    LOGGER.info('    - KAFKA_NAME: {}'.format(pytest.KAFKA_NAME))
    LOGGER.info('    - TOPIC_NAME: {}'.format(pytest.TOPIC_NAME))
    LOGGER.info('    - BILLING_MODEL: {}'.format(pytest.BILLING_MODEL))
    LOGGER.info('    - KAFKA_INSTANCE_PLAN: {}'.format(pytest.KAFKA_INSTANCE_PLAN))
    LOGGER.info('    - CLOUD_PROVIDER: {}'.format(pytest.CLOUD_PROVIDER))
    LOGGER.info('    - REGION: {}'.format(pytest.REGION))
    LOGGER.info('    - API_BASE_HOST: {}'.format(pytest.API_BASE_HOST))

    def teardown():
        LOGGER.info('FINISH')
    request.addfinalizer(teardown)
    
    return
