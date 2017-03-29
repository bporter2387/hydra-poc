#!/usr/bin/env python


import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# disable warnings for ssl cert
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)




# FIRST WE NEED TO GENERATE AN ADMIN TOKEN FOR HYDRA
# print("Generating a Warden Token for authorizing Tokens...")
#
# auth_url = "https://localhost:4444/oauth2/token"
# headers = {'content-type': 'application/x-www-form-urlencoded'}
# payload = {
#     'grant_type': 'client_credentials',
#     'scope': 'hydra'
# }
# resp = requests.post(
#         auth_url,
#         auth=('admin', 'demo-password'),
#         headers=headers,
#         data=payload,
#         verify=False
#     )
#
# access_token = resp.json()["access_token"]


access_token = "86169T0HdjZg0BgmKeoQ9rLD_eOrQ5BPJk-BdJaX1Ro.HOsS7tQwQJ_ugpW1m84bGY26jfYzltnBmUb3hUd2p3c"

print("\nYour token: %s\n\n" % (access_token))




# print("Creating a default access policy...")
#
# auth_url = "https://localhost:4444/policies"
# policy_payload = {
#     "description": "Axial Member",
#     "subjects": ["role:member"],
#     "actions" : ["read", "create", "update", "replace"],
#     "effect": "allow",
#     "resources": [
#         "some.domain.com:accounts:<.*>",
#         "some.domain.com:users:<.*>",
#         "some.domain.com:events:<.*>",
#         "some.domain.com:me:<.*>"
#     ],
#     "conditions": {}
#     }
# policy_headers = {
#     'content-type': 'application/json',
#     'accept': 'application/json;v=1',
#     "Authorization":"Bearer {}".format(access_token)
#     }
#
# resp = requests.post(
#             auth_url,
#             headers=policy_headers,
#             json=policy_payload,
#             verify=False)
#
# print("Policy Created: %s" % resp.json())






# CREATE CLIENT ID AND SECRET (Axial app)
auth_url = "https://localhost:4444/clients"
payload = {
  "owner": "my.email@gmail.com",
  "scope": "read replace update delete create",
  "public": False,
  "client_name": "user-public-id",
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
}

headers = {
    'content-type': 'application/json',
    "Authorization":"Bearer {}".format(access_token)
    }
resp = requests.post(
    auth_url,
    headers=headers,
    json=payload,
    verify=False)

print("Client JSON: %s\n" % (resp.json()))
print("Client ID: %s\nClient Secret: %s\n\n" % (resp.json()["id"], resp.json()["client_secret"]))







# Create a token for the Axial App
print("Creating a token for the Axial App (credentials above)")

auth_url = "https://localhost:4444/oauth2/token"
headers = {'content-type': 'application/x-www-form-urlencoded'}
payload = {
    'grant_type': 'client_credentials',
    'scope': 'read'
}
resp = requests.post(
        auth_url,
        auth=(resp.json()["id"], resp.json()["client_secret"]),
        headers=headers,
        data=payload,
        verify=False
    )

app_access_token = resp.json()["access_token"]

print("App JSON: %s" % (resp.json()))
print("App Access Token: %s\n\n" % (app_access_token))






auth_url = "https://localhost:4444/warden/token/allowed"
print("Checking to see if we have access..\n")
allowed_payload = {
      "scopes": ["read"],
      "token": app_access_token,
      "resource": "some.domain.com:accounts:some-account",
      "action": "read"
    }
print("Payload: %s\n" % (allowed_payload))
allowed_headers = {
    'content-type': 'application/json',
    "Authorization":"Bearer {}".format(access_token)
    }
resp = requests.post(
    auth_url,
    headers=allowed_headers,
    json=allowed_payload,
    verify=False)

print("Allowed Response: %s" % (resp.json()))
