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
	-d scope=hydra.warden \
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








------------------------------------------------------------------



### Generate a new Policy for Authorization
> Using the **hydra.policies** access token as the Authorization header, Create a new Policy. These policies are global.

```
curl -s -k \
  -X POST \
  -H "Content-Type: application/json" \
	-H "Authorization:bearer 78luCtLzDihRt_NetmlTcehpANLQkqUvXkOoMRDOcd0.q3YCAiNwqjL6T8Wf6_dgbrgF18NebzBGbDReEIiFBfg" \
  -d '@policy.json' \
  "https://localhost:4444/policies" | jq .
```

*Example policy.json*
> This policy says: Users Peter or Giff and Users in the member group are allowed read, create, update, and replace all accounts and users if the server performing the action is from one of our AWS instances (10.0.0.0/16)
>`users:<[peter|brett]>` implies users *peter* or *giff*

```
{
  "description": "Some Member",
  "subjects": ["users:<[peter|giff]>", "groups:member"],
  "actions" : ["read", "<[create|update]>", "replace"],
  "effect": "allow",
  "resources": [
    "resources:accounts:<.*>",
    "resources:users:<.*>"
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
  "description": "Some Member",
  "subjects": [
    "users:<[peter|giff]>",
    "admin",
    "groups:member"
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
	-H "Authorization:bearer oljNZBNToJlX_HG4jHgnEqbxoaAgPl5lB-SoV-0P_IQ.HTubih0M0_OCnmVMgOHCWqlStTMTBnxH16Gj_rBSOoQ" \
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












> *Note: The backend will generate this on successful login of the user and set a JWT cookie with the access token for the Frontend to use*
























# Scenario 2 (Future 3.0)

### Generate an admin token that has access to create Client ID / Client Secret sets
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



### Using this admin client-enabled access token, create a Client Set to be sent to the Master Account user

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


> Once you have the client ID and secret, you can generate an access_token for one of the scopes
> defined in the creation above (read write edit foobar etc..)

> Generate an access token using the client credentials above for read access only
```
curl -s -k -X POST \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d grant_type=client_credentials \
  -d scope=read \
  -u '436ea2f1-3fa9-418a-b8bf-7d83a0a63fec:4bn0%Vm&=fvd' \
  https://localhost:4444/oauth2/token | jq .
```







### Flow of access token distribution (Scenario 1)
- USER LOGS IN
- ACCESS TOKEN COOKIE IS SET
- REQUEST API ENDPOINT WITH ACCESS TOKEN AND RESOURCE REQUEST (ie /user/me). FRONTEND WILL KNOW WHICH ENDPOINTS IT CAN AND CANNOT HIT IF ANY
- MICROSERVICE AUTHORIZES WITH HYDRA (request_authorizer)
- IF ALLOWED, CONTINUE WITH REQUEST AND RETURN DATA, OTHERWISE RETURN 401



#### Set cookie with access token in this file
https://github.com/axialmarket/axm/lib/python2.7/site-packages/authlib/auth/lib.py

#### Change request to point to Hydra service
https://github.com/axialmarket/axial-service-lib/blob/master/axial/service/middleware/request_authorizer.py
