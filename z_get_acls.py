import time
import rhoas_kafka_instance_sdk
from rhoas_kafka_instance_sdk.api import acls_api
from rhoas_kafka_instance_sdk.model.sort_direction import SortDirection
from rhoas_kafka_instance_sdk.model.acl_binding_list_page import AclBindingListPage
from rhoas_kafka_instance_sdk.model.error import Error
from pprint import pprint
from auth.rhoas_auth import get_access_token
# Defining the host is optional and defaults to http://localhost
# See configuration.py for a list of all supported configuration parameters.
configuration = rhoas_kafka_instance_sdk.Configuration(
    host = "http://localhost"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization (JWT): Bearer
configuration = rhoas_kafka_instance_sdk.Configuration(
    access_token = 'YOUR_BEARER_TOKEN'
)
offline_token = ""

# Configure OAuth2 access token for authorization: OAuth2
configuration = rhoas_kafka_instance_sdk.Configuration(
    host = ""
)
tk = {}
tk = get_access_token(offline_token=offline_token)
configuration.access_token = tk['access_token']

# Enter a context with an instance of the API client
with rhoas_kafka_instance_sdk.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = acls_api.AclsApi(api_client)
    resource_type = None # bool, date, datetime, dict, float, int, list, str, none_type | ACL Resource Type Filter (optional)
    resource_name = "resourceName_example" # str | ACL Resource Name Filter (optional)
    pattern_type = None # bool, date, datetime, dict, float, int, list, str, none_type | ACL Pattern Type Filter (optional)
    principal = "User:*" # str | ACL Principal Filter. Either a specific user or the wildcard user `User:*` may be provided. - When fetching by a specific user, the results will also include ACL bindings that apply to all users. - When deleting, ACL bindings to be delete must match the provided `principal` exactly. (optional) if omitted the server will use the default value of ""
    operation = None # bool, date, datetime, dict, float, int, list, str, none_type | ACL Operation Filter. The ACL binding operation provided should be valid for the resource type in the request, if not `ANY`. (optional)
    permission = None # bool, date, datetime, dict, float, int, list, str, none_type | ACL Permission Type Filter (optional)
    page = 1 # int | Page number (optional)
    size = 1 # int | Number of records per page (optional)
    order = SortDirection("asc") # SortDirection | Order items are sorted (optional)
    order_key = None # bool, date, datetime, dict, float, int, list, str, none_type |  (optional)

    # example passing only required values which don't have defaults set
    # and optional values
    try:
        # List ACL bindings
        api_response = api_instance.get_acls( page=page, size=size, order=order, order_key=order_key, async_req=True)
        api_response = api_response.get()
        print(api_response)
    except rhoas_kafka_instance_sdk.ApiException as e:
        print("Exception when calling AclsApi->get_acls: %s\n" % e)
        