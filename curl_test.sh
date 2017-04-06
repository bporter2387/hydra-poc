#!/bin/bash

RESOURCE_REQUEST=${RESOURCE_REQUEST:-"read:content:published_from:user:<.*>"}
ACTION=${ACTION:-"read"}

am_i_allowed() {
  ALLOWED=$(curl -k -s \
  	-H "Content-Type: application/json" \
  	-H "Authorization:bearer $HYDRA_TOKEN" \
  	--data '{
      "token": "$CLIENT_ACCESS_TOKEN",
      "resource": "$RESOURCE_REQUEST",
      "action": "$ACTION",
      "context": {
        "subject": "$CLIENT_ID"
      }
    }' \
    https://localhost:4444/warden/token/allowed | jq .allowed)
    if [[ $ALLOWED == "true" ]]; then
      echo "Yes you can access this resource"
    else
      echo "$CLIENT_ACCESS_TOKEN is FORBIDDEN!"
    fi
}


get_permissions() {
  # Check token
  PERMISSIONS=$(curl -k -s \
      --request POST \
       --header "Content-Type: application/x-www-form-urlencoded" \
       --header "Authorization: Bearer $HYDRA_TOKEN" \
       -d "token=$CLIENT_ACCESS_TOKEN" \
       https://localhost:4444/oauth2/introspect | jq .)
  printf "Permissions:\n\n $PERMISSIONS \n\n"
}

if [[ ! -z $CLIENT_ACCESS_TOKEN ]]; then
  am_i_allowed
  get_permissions
fi




# Create master Hydra token to verify requests
if [[ -z $HYDRA_TOKEN ]]; then
  HYDRA_TOKEN=$(curl -s -k -X POST \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d grant_type=client_credentials \
        -d scope=hydra \
        -u 'admin:demo-password' \
        https://localhost:4444/oauth2/token | jq .access_token)
fi



# Create a new App/Client
if [[ -z $CLIENT_ID ]]; then
  CLIENT_ID=$(curl -s -k \
    -X POST \
  	-H "Content-Type: application/json" \
  	-H "Authorization: bearer $HYDRA_TOKEN" \
  	-d '{
      "owner": "my.email@gmail.com",
      "scope": "role:user staff:admin",
      "public": false,
      "client_name": "Global Authorization Token Warden",
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
    }' \
    https://localhost:4444/clients | jq .id)
fi

printf "CLIENT_ID: $CLIENT_ID \n\n"



# Create Policy if there isn't one
if [[ -z $POLICY_ID ]]; then
  POLICY_ID=$(curl -s -k \
    -X POST \
    -H "Content-Type: application/json" \
  	-H "Authorization:bearer $HYDRA_TOKEN" \
    -d '{
        "description": "Anonymous User",
        "subjects": ["$CLIENT_ID"],
        "actions" : ["$ACION"],
        "effect": "allow",
        "resources": [
          "read:accounts:<.*>",
          "read:users:<.*>",
          "read:content:published_from:user:<.*>"
        ],
        "conditions": {
          "subject": {
              "type": "EqualsSubjectCondition"
          }
        }
      }' "https://localhost:4444/policies" | jq .id)
fi

# Get Policy
POLICY=$(curl -s -k \
  -X GET \
  -H "Content-Type: application/json" \
  -H "Authorization:bearer $HYDRA_TOKEN" \
  "https://localhost:4444/policies/$POLICY_ID" | jq .)


printf "POLICY_ID - $POLICY_ID\n"
printf "POLICY - $POLICY\n"







if [[ ! -z $CLIENT_ACCESS_TOKEN || $ALLOWED != "true" ]]; then

  CLIENT_ACCESS_TOKEN=$(curl -s -k -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d grant_type=client_credentials \
    -d scope=my_custom_scope \
    -u '40ff2609-123a-45c5-abad-759829a3423d:>cHX$V;pyEOX' \
    https://localhost:4444/oauth2/token | jq .access_token)

  printf "NEW CLIENT_ACCESS_TOKEN: $CLIENT_ACCESS_TOKEN \n"

fi

am_i_allowed
get_permissions
