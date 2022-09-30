# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
class ModuleDocFragment(object):
    # Standard documentation
    DOCUMENTATION = r'''
  notes:
    - This module will work best if used in a Python virtual environment.
    - All modules require an 'OFFLINE_TOKEN' environment variable to be set with a valid token. This 
      is used to authenticate the user. The token is an OpenShift Cluster Manager API Token and can be 
      found here https://console.redhat.com/openshift/token
    - This module depends on the 'rhoas-sdk' Python package. This package can be installed using the
      'pip' command. 
    - 'pip install rhoas-sdksq'
  options:
    rhosak_api_key:
      description: The API key to use for authentication.
      OFFLINE_TOKEN: 'OFFLINE_TOKEN'
        
    '''

    # Additional section
    OTHER = r'''
    options:
      There are some depencdanceies that are required for this module to work. These are:
        - "python >= 3.9"
        - "rhoas-sdks >= 0.3.1"
        
    - There are some depencdanceies that are required for this module to work. These are:
      - "python >= 3.9"
      - "rhoas-sdks >= 0.3.1"
    - Dependencies can be installed using pip:
      - "pip install rhoas-sdks"
    All dependencies can be installed using pip:
        - "pip install python"
        - "pip install rhoas-sdks"
    '''