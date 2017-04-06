#!/usr/bin/env python


import requests
import os
import json
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
# if HYDRA_TOKEN isn't set in environment, then create one
access_token = None
try:
    access_token = os.environ['HYDRA_TOKEN']
except:
    pass

if not access_token:

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
client_id = None
client_secret = None
try:
    client_id = os.environ['CLIENT_ID']
    client_secret = os.environ['CLIENT_SECRET']
except:
    pass

if not client_id or not client_secret:

    client_resp = requests.post(
        "{}/clients".format(base_url),
        headers={
            'content-type': 'application/json',
            "Authorization":"Bearer {}".format(access_token)
            },
        json={
          "owner": "my.email@gmail.com",
          "scope": "role:user role:admin",
          "public": False,
          "client_name": "Company X's master account",
          "redirect_uris": [
            "https://some.domain.net/home",
            "https://some.domain.net/some/other/restricted/home"
          ],
          "grant_types": [
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


    print("CLIENT INFORMATION")
    print(json.dumps(client_resp.json(), indent=4, sort_keys=True))
    print("\n\n")
    client_id = client_resp.json()["id"]
    client_secret = client_resp.json()["client_secret"]

    print("\
    Client ID: %s \n\
    Client Secret: %s \n\n\
    \
    You may want to run \n\
    export CLIENT_ID=%s \n\
    export CLIENT_SECRET=%s \n\n" % (client_id, client_secret, client_id, client_secret))

else:
    print('USING YOUR ENVIRONMENT CLIENT CREDENTIALS')






#
#
# Create an access policy for the App. The subject must contain the client ID
#
#
policy_id = None
try:
    policy_id = os.environ['POLICY_ID']
except:
    pass

policy_headers = {
    'content-type': 'application/json',
    'accept': 'application/json;v=1',
    "Authorization":"Bearer {}".format(access_token)
    }

if not policy_id:

    print("Creating a default access policy...")
    auth_url = "{}/policies".format(base_url)
    policy_payload = {
      "description": "Admin User",
      "subjects": ["role:admin", client_id],
      "actions" : ["read", "create", "update", "delete"],
      "effect": "allow",
      "resources": [
        "read:accounts:<.*>",
        "read:users:<.*>",
        "<.*>:my:projects:<.*>",
        "<.*>:my:campaigns:<.*>"
      ],
      "conditions": {}
    }

    policy_resp = requests.post(
                auth_url,
                headers=policy_headers,
                json=policy_payload,
                verify=False)

    print("Policy Created: \n")
    print(json.dumps(policy_resp.json(), indent=4, sort_keys=True))


else:
    auth_url = "{}/policies/{}".format(base_url, policy_id)

    policy_resp = requests.get(
            auth_url,
            headers=policy_headers,
            verify=False)

    print("Using Policy: \n")
    print(json.dumps(policy_resp.json(), indent=4, sort_keys=True))








#
#
# Create a token for the Axial App (using client id and secret)
#
#
client_access_token = None

try:
    client_access_token = os.environ['CLIENT_ACCESS_TOKEN']
except:
    pass

if not client_access_token:
    print("...creating a unique client access token.. (Logged in user)")

    auth_url = "{}/oauth2/token".format(base_url)
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    payload = {
        'grant_type': 'client_credentials',
        'scope': "role:admin"
    }
    client_resp = requests.post(
            auth_url,
            auth=(client_id, client_secret),
            headers=headers,
            data=payload,
            verify=False
        )

    client_access_token = client_resp.json()["access_token"]

    print("...client access token created...")
    print(json.dumps(client_resp.json(), indent=4, sort_keys=True))

    print("CLIENT_ACCESS_TOKEN: %s\n" % (client_access_token))








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
            'token': '{}'.format(client_access_token),
        },
        verify=False
    )
print("...checking to see if the token is valid..")
print(json.dumps(introspect_resp.json(), indent=4, sort_keys=True))
print("\n\n")
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
print("...checking to see if the token has access..")
access_resp = requests.post(
    "{}/warden/token/allowed".format(base_url),
    headers={
        'content-type': 'application/json',
        "Authorization":"Bearer {}".format(access_token)
        },
    json={
          "scopes": ["role:admin"],
          "token": client_access_token,
          "resource": "read:accounts:some-account",
          "action": "read",
          "context": {}
        },
    verify=False)

print(json.dumps(access_resp.json(), indent=4, sort_keys=True))
