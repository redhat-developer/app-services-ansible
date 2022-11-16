# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
class ModuleDocFragment(object):
    # Standard documentation
    DOCUMENTATION = r'''
  notes:
    - This module will work best if used in a Python virtual environment.
    - This module also requires an 'OFFLINE_TOKEN' to be used with for authentication with the Red Hat 
      OpenShift Application Services API. The token can be passed in as an argument or alternatively
      an 'OFFLINE_TOKEN' environment variable can be set with a valid token.
      This is used to authenticate the user. The token is an OpenShift Token and can be 
      found here https://console.redhat.com/openshift/token
    - This module depends on the 'rhoas-sdks' Python package. This package can be installed using the
      'pip' command. 
    - 'pip install rhoas-sdks'
    - or 'pip install rhoas-sdks --force-reinstall' to make sure you have the latest version of the SDKs available
  options:
    openshift_offline_token:
      description: The API key to use for authentication.
      openshift_offline_token: 'OFFLINE_TOKEN'
        
    '''

    # Additional section
    OTHER = r'''
    options:
      There are some dependencies that are required for this module to work. These are:
        - "python >= 3.9"
        - "rhoas-sdks >= 0.3.1"
        -  "python-dotenv"
        
    - There are some dependencies that are required for this module to work. These are:
      - "python >= 3.9"
      - "rhoas-sdks >= 0.3.1"
    - Dependencies can be installed using pip:
      - "pip install rhoas-sdks"
      - "pip install python-dotenv"
    '''