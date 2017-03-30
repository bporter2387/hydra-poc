# Authorization 2.0

Bootstrap your test environment
```
docker-compose up -d
```




------------------------------------------------------------------



# ADMIN TOKENS


### Generate Access Token (`hydra.warden`)
> Using the **admin** username and **demo-password** password we defined in the FORCE_ROOT_CLIENT_CREDENTIALS environment variable in docker-compose.yml, we'll generate an admin access token that is allowed to check if a token has access to a resource. We could use **scope=hydra** to allow all hydra permissions to this token, but we'll keep them separate for now.


```
curl -s -k -X POST \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d grant_type=client_credentials \
	-d scope=hydra \
	-u 'admin:demo-password' \
	https://localhost:4444/oauth2/token | jq .
```



> ...response data from Hydra

```
{
  "access_token": "uBkl78-i7SsaYraHfSsFRLkwYKV-r7R6iabeu6QHZ28.hJ6XiAele_nrouprBkvlAnhejuWQdg0lCEW7D1YcI_4",
  "expires_in": 3599,
  "scope": "hydra.warden",
  "token_type": "bearer"
}
```






------------------------------------------------------------------





### Generate Access Token (`hydra.policies`)
> Similarly to the warden access token, we'll create a token for Policy API Usage. This allows us to CREATE, GET, & DELETE policies

```
curl -s -k \
	-X POST \
	-H "Content-Type: application/x-www-form-urlencoded" \
	-d grant_type=client_credentials \
	-d scope=hydra.policies \
	-u 'admin:demo-password' \
	https://localhost:4444/oauth2/token | jq .
```

> ...response data from Hydra

```
{
  "access_token": "uBkl78-i7SsaYraHfSsFRLkwYKV-r7R6iabeu6QHZ28.hJ6XiAele_nrouprBkvlAnhejuWQdg0lCEW7D1YcI_4",
  "expires_in": 3599,
  "scope": "hydra.policies",
  "token_type": "bearer"
}
```








### Generate an admin token that has access to create Client ID / Client Secret sets (Apps)
```
curl -s -k \
  -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d grant_type=client_credentials \
  -d scope=hydra.clients \
  -u 'admin:demo-password' \
  https://localhost:4444/oauth2/token | jq .
```

> ...response from Hydra

```
{
	"access_token": "8WyvslooM8JK-Q4kg5iVC37nEGKIg2xwaJbazB-5zt8.kzLsucLs_69cd4gdjmNt7OKDhcst4r2MfqzAT4wXPr4",
	"expires_in": 215999,
	"scope": "hydra.clients",
	"token_type": "bearer"
}
```



### Using this admin/hydra client-enabled access token, create a Client Set (App)

> GENERATE THE CLIENT SET

```
curl -s -k \
  -X POST \
	-H "Content-Type: application/json" \
	-H "Authorization: bearer 8WyvslooM8JK-Q4kg5iVC37nEGKIg2xwaJbazB-5zt8.kzLsucLs_69cd4gdjmNt7OKDhcst4r2MfqzAT4wXPr4" \
	-d '@client.json' \
  https://localhost:4444/clients | jq .
```




> Example client.json

```
{
  "owner": "brett.porter@axial.net",
  "scope": "read replace update delete create",
  "public": false,
  "client_name": "user-public-id",
  "redirect_uris": [
    "https://integration.axial.net/home",
    "https://integration.axial.net/some/other/restricted/home"
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
  "client_uri": "https://staging.axial.net/company/admin",
  "contacts": [
    "brett.porter@axial.net"
  ]
}

```

> ...response from Hydra

```
{
  "id": "436ea2f1-3fa9-418a-b8bf-7d83a0a63fec",
  "client_name": "user-public-id",
  "client_secret": "4bn0%Vm&=fvd",
  "redirect_uris": [
    "https://integration.axial.net/home",
    "https://integration.axial.net/some/other/restricted/home"
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
  "scope": "read replace update delete create",
  "owner": "brett.porter@axial.net",
  "policy_uri": "",
  "tos_uri": "",
  "client_uri": "https://staging.axial.net/company/admin",
  "logo_uri": "",
  "contacts": [
    "brett.porter@axial.net"
  ],
  "public": false
}
```






------------------------------------------------------------------



### Generate a new Policy for Authorization
> Using the **hydra.policies** access token as the Authorization header, Create a new Policy. These policies are linked to the client ID.
> The client ID must be in the "subjects" field

```
curl -s -k \
  -X POST \
  -H "Content-Type: application/json" \
	-H "Authorization:bearer hydra.policies.token.here" \
  -d '@policy.json' \
  "https://localhost:4444/policies" | jq .
```

*Example policy.json*
> Policies created with a client ID in the `subjects` field are linked to that client. So this means any tokens created by
> that client ID/Secret pair will authorize against policies created with the client ID as the subject.
> For `global` policies, you can use arbitrary terms for authorization such as `groups:moderators`.
>  
> This policy says: the `administrator` user, anyone in the `moderators` group, and all users provided with a token from the client ID 436ea2... are allowed read, create, update, and replace all accounts and
> users if the server performing the action is from one of our AWS instances (10.0.0.0/16)
> actions `<[create|update]>` implies *create* or *update*
> NOTE: adding arbitrary items in the subject field enables any and all tokens to authorize using the /warden/allowed endpoint.
> Authorizing tokens against policies requires a client ID in the subject field and authorizes using the /warden/token/allowed endpoint.

```
{
  "description": "Users with limited privileges",
  "subjects": ["436ea2f1-3fa9-418a-b8bf-7d83a0a63fec", "groups:moderators", "user:administrator"],
  "actions" : ["read", "<[create|update]>", "replace"],
  "effect": "allow",
  "resources": [
    "some.domain.com:accounts:<.*>",
    "some.domain.com:users:<.*>"
  ],
  "conditions": {
    "remoteIP": {
        "type": "CIDRCondition",
        "options": {
            "cidr": "10.0.0.1/16"
        }
    }
  }
}

```

> ...response from hydra

```
{
  "id": "13a146fe-0b62-4775-8ffb-0af8971aca9e",
  "description": "Users with limited privileges",
  "subjects": [
    "436ea2f1-3fa9-418a-b8bf-7d83a0a63fec",
    "groups:moderators",
    "user:administrator"
  ],
  "effect": "allow",
  "resources": [
    "some.domain.com:accounts:<.*>",
    "some.domain.com:users:<.*>"
  ],
  "actions": [
    "read",
    "<[create|update]>",
    "replace"
  ],
  "conditions": {
    "remoteIP": {
      "type": "CIDRCondition",
      "options": {
        "cidr": "10.0.0.1/16"
      }
    }
  }
}
```











> Using a token generated with **hydra.warden** scope as the Authorization bearer, we'll send the following data `query_with_token.json` to check if the `token` token has `action` privileges to the `resource` resources within the following `scopes` (read) given the `context` matching the conditions in one of the policies created.

```
curl -k -s \
	-H "Content-Type: application/json" \
	-H "Authorization:bearer 1NLbBOmdYZs8fA4RC_iYcczHNfAtvpCeF6OhDGUXLkk.-x0JcjsbbmUGa1ezs5Gn8GGo-JDjDtuEl8uchjx_62Q" \
	--data '@query_with_token.json' \
  https://localhost:4444/warden/token/allowed | jq .
```

*Example query_with_token.json*
```
{
  "scopes": ["read"],
  "token": "-Hes4s_tXRwHoMpiRZi0XvCvuwswHPu9EcWUFs0T5lE.wGXrT8VLWzAbQtgmPOTCtkQFvdJ6uJ3pUtLjREnpcQ0",
  "resource": "some.domain.com:accounts:some-account",
  "action": "replace",
  "context": {
    "remoteIP": "10.0.0.45"
  }
}

```
