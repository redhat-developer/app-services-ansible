from keycloak import KeycloakOpenID

# Configure client
keycloak_openid = KeycloakOpenID(server_url="https://sso.redhat.com/auth/",
                                 client_id="rhoas-cli-prod",
                                 realm_name="redhat-external")

# Get WellKnow
config_well_known = keycloak_openid.well_known()

offlineToken=""

# Refresh token
token = keycloak_openid.refresh_token(offlineToken)

print(token)


 