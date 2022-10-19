#!/usr/bin/python
# -*- coding: utf-8 -*-

# Apache License, v2.0 (https://www.apache.org/licenses/LICENSE-2.0)
from os import environ
from auth.rhoas_auth import get_access_token

def get_offline_token(module_param_offline_token):
    if module_param_offline_token is None or module_param_offline_token == '':
        return get_access_token(offline_token=None)['access_token']
    else:
        return get_access_token(module_param_offline_token)['access_token']