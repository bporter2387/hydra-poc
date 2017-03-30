#!/usr/bin/env python


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# disable warnings for ssl cert
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

base_url = "https://localhost:4444"


#
#
# Create an Admin token that's allowed to perform administrative tasks in Hydra
#   hydra.policies - access to create/get/delete policies
#   hydra.warden - access to create/check/delete tokens
#       note: clients can also create tokens with limited access to their own resources
#   hydra.clients - access to create client ID's and secrets
#   hydra - all of the above
#
#
print("Generating a Warden Token for authorizing Tokens...")

auth_url = "{}/oauth2/token".format(base_url)
admin_resp = requests.post(
        auth_url,
        auth=('admin', 'demo-password'),
        headers={'content-type': 'application/x-www-form-urlencoded'},
        data={
            'grant_type': 'client_credentials',
            'scope': 'hydra'
        },
        verify=False
    )

access_token = admin_resp.json()["access_token"]
print("\nAdmin Hydra Token: %s\n\n" % (access_token))










#
#
# Create a new "App" (client ID and secret)
#
#
client_resp = requests.post(
    "{}/clients".format(base_url),
    headers={
        'content-type': 'application/json',
        "Authorization":"Bearer {}".format(access_token)
        },
    json={
      "owner": "my.email@gmail.com",
      "scope": "all-members",
      "public": False,
      "client_name": "Company X's master account",
      "redirect_uris": [
        "https://some.domain.net/home",
        "https://some.domain.net/some/other/restricted/home"
      ],
      "grant_types": [
        "implicit",
        "refresh_token",
        "authorization_code",
        "password",
        "client_credentials"
      ],
      "response_types": [
        "code",
        "token",
        "id_token"
      ],
      "client_uri": "https://some.domain.net/company/admin",
      "contacts": [
        "my.email@gmail.com"
      ]
    },
    verify=False)

print("Client Object: %s\n" % (client_resp.json()))
client_id = client_resp.json()["id"]
client_secret = client_resp.json()["client_secret"]

print("Client ID: %s\nClient Secret: %s\n\n" % (client_id, client_secret))











#
#
# Create an access policy for the App. The subject must contain the client ID
#
#
print("Creating a default access policy...")

auth_url = "{}/policies".format(base_url)
policy_payload = {
    "description": "Axial Member",
    "subjects": [client_id],
    "actions" : ["read", "replace", "delete"],
    "effect": "allow",
    "resources": [
        "some.domain.com:accounts:<.*>",
        "some.domain.com:users:<.*>"
    ],
    "conditions": {}
    }
policy_headers = {
    'content-type': 'application/json',
    'accept': 'application/json;v=1',
    "Authorization":"Bearer {}".format(access_token)
    }

policy_resp = requests.post(
            auth_url,
            headers=policy_headers,
            json=policy_payload,
            verify=False)

print("Policy Created: %s\n\n" % policy_resp.json())









#
#
# Create a token for the Axial App (using client id and secret)
#
#
print("Creating a token for the Axial App (credentials above)\n")

auth_url = "{}/oauth2/token".format(base_url)
headers = {'content-type': 'application/x-www-form-urlencoded'}
payload = {
    'grant_type': 'client_credentials',
    'scope': 'all-members'
}
app_resp = requests.post(
        auth_url,
        auth=(client_id, client_secret),
        headers=headers,
        data=payload,
        verify=False
    )

app_access_token = app_resp.json()["access_token"]

print("App JSON: %s\n" % (app_resp.json()))
print("App Access Token: %s\n\n" % (app_access_token))














#
#
# Check to make sure token is still valid and active
#
#

auth_url = "{}/oauth2/introspect".format(base_url)
introspect_resp = requests.post(
        auth_url,
        headers={
            'content-type': 'application/x-www-form-urlencoded',
            'Authorization': 'bearer {}'.format(access_token)
        },
        data={
            'token': '{}'.format(app_access_token),
        },
        verify=False
    )
print("Token Validity: %s\n\n" % (introspect_resp.json()))

# curl -s -k -X POST \
#   -H "Content-Type: application/x-www-form-urlencoded" \
#   -H "Authorization: bearer G9hI_-TUGApjCSQVJAMltbeYwMPhzHQ35XyJtuRVnYg.wzq2CoRAnaMLE8AzYQTA1vnt83SQiXUYvCGdiGCFCZ8" \
#   -d "token=G9hI_-TUGApjCSQVJAMltbeYwMPhzHQ35XyJtuRVnYg.wzq2CoRAnaMLE8AzYQTA1vnt83SQiXUYvCGdiGCFCZ8" \
#   https://localhost:4444/oauth2/introspect | jq .












#
#
# Check the app token to make sure it has access to the requested resource
#
#
print("Checking to see if we have access..\n")
access_resp = requests.post(
    "{}/warden/token/allowed".format(base_url),
    headers={
        'content-type': 'application/json',
        "Authorization":"Bearer {}".format(access_token)
        },
    json={
          "scopes": ["all-members"],
          "token": app_access_token,
          "resource": "some.domain.com:accounts:some-account",
          "action": "read",
          "context": {}
        },
    verify=False)

print("Allowed Access Response: %s\n\n" % (access_resp.json()))
