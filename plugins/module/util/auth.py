from keycloak import KeycloakOpenID
from os import environ;

def get_access_token():
    offlineToken = environ.get('OFFLINE_TOKEN')
    # Configure client
    keycloak_openid = KeycloakOpenID(server_url="https://sso.redhat.com/auth/",
                                 client_id="cloud-services",
                                 realm_name="redhat-external")
    # Refresh token
    token = keycloak_openid.refresh_token(offlineToken)
    return token




 