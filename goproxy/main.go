package main

import (
	"bytes"
	"crypto/tls"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"strings"

	"net/http"

	"github.com/gin-gonic/gin"
)

func main() {
	router := gin.Default()
	router.Any("/*action", authorize)
	router.Run(":8080")
}

// Allowed - is allowed
type Allowed struct {
	Allowed bool `json:"allowed"`
}

// AuthPayload -
type AuthPayload struct {
	subject  string
	resource string
	action   string
	context  Context
}

// Context -
type Context struct {
	subject string
}

// '{"subject":"role:anonymous", "resource":"read:accounts:axial","action":"read", "context": {"subject":"role:anonymous"}}'

func authorize(c *gin.Context) {

	var w http.ResponseWriter
	authorized := authorizeHandler(w, c.Request)

	// if auth
	if authorized {
		fmt.Printf("%v", "...sending request to microservice...\n\n")
		// data := []string{}
		// "data":   {"last_name": "Porter", "rank": 49, "type_code": "axial_employee", "headshot": null, "created_at": 1438617928000, "bio": "null", "email": "brett.porter@axial.net", "account": {"id": "a2543098e29c11e2940012313b0a607d", "license": {"account_id": 33206, "msgs_sent": 2, "msg_quota": 7000, "is_call_button_enabled": true}}, "first_name": "Brett", "title": "", "updated_at": 1491680540000, "linkedin_url": null, "last_activity_at": 1491680540000, "id": "759df44239f911e5a5d322000b680490"},
		microserviceHandler(w, c.Request)
		c.JSON(http.StatusUnauthorized, gin.H{
			"authorized": true,
		})
		fmt.Printf("%v", "...sending request to microservice...")

	} else {
		c.JSON(http.StatusUnauthorized, gin.H{"authorized": false})
	}

	// content := gin.H{
	// 	"result": "{some: data}",
	// }

	// for k, v := range

}

func authorizeHandler(w http.ResponseWriter, req *http.Request) bool {

	// Print the body for verbosity
	x, _ := ioutil.ReadAll(req.Body)
	fmt.Printf("\nBODY:\n%v\n\n", string(x))

	// you can reassign the body if you need to parse it as multipart
	// req.Body = ioutil.NopCloser(bytes.NewReader(body))

	// create a new url from the raw RequestURI sent by the client
	// url := fmt.Sprintf("%s://%s%s", proxyScheme, proxyHost, req.RequestURI)
	url := "https://hydra:4444/warden/allowed"

	// Print custom headers
	// fmt.Printf("%v\n", "HEADERS")
	// fmt.Printf("X-IamBatmanLetMeIn: %v\n", req.Header.Get("X-IamBatmanLetMeIn"))
	// fmt.Printf("X-ClientAccessToken: %v\n", req.Header.Get("X-ClientAccessToken"))

	// Parse Custom headers
	result := strings.Split(req.Header.Get("X-IamBatmanLetMeIn"), ":")
	action := result[0]
	resource := result[1]
	resourceID := result[2]

	fmt.Printf("ACTION: %v\n", action)
	fmt.Printf("RESOURCE: %v\n", resource)
	fmt.Printf("RESOURCE_ID: %v\n", resourceID)

	// Build Auth Payload
	// context := Context{
	// 	subject: "role:anonymous",
	// }

	authPayload := AuthPayload{
		subject:  "role:anonymous",
		action:   action,
		resource: action + ":" + resource + ":" + resourceID,
		context: Context{
			subject: "role:anonymous",
		},
	}

	fmt.Printf("PAYLOAD: %v\n\n", authPayload)

	// s := `{ "votes": { "option_A": "3" } }`
	// data := &Data{
	//     Votes: &Votes{},
	// }
	// err := json.Unmarshal([]byte(s), data)

	// context:    []byte(`{"subject": "role:anonymous"}`),
	// authPayload.action = action
	// authPayload.resource = resource
	// authPayload.resourceID = resourceID
	// var authTmp AuthPayload
	// j, _ := json.Unmarshal(authPayload, &authTmp)
	// fmt.Printf("JSON UNM: %v\n\n", j)
	// b, err := json.Marshal(authPayload)
	// if err != nil {
	// 	fmt.Printf("%v\n", "ERROR!!")
	// }

	cfg := &tls.Config{
		InsecureSkipVerify: true,
	}
	client := &http.Client{}
	client.Transport = &http.Transport{
		TLSClientConfig: cfg,
	}

	payloadStr := fmt.Sprintf("{\"subject\": \"%v\", \"action\":\"%v\", \"resource\": \"%v\", \"context\":{\"subject\":\"%v\"}}", "role:anonymous", action, action+":"+resource+":"+resourceID, "role:anonymous")
	var jsonStr = []byte(payloadStr)
	proxyreq, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonStr))

	// pr, _ := ioutil.ReadAll(proxyreq.Body)
	// fmt.Printf("\nPROXY BODY:\n%v\n\n", string(pr))

	// var jsonStr = []byte(x)
	// proxyreq, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonStr))
	proxyreq.Header.Set("Authorization", "Bearer 6PtUXAFfTpgw_H0ACM7oaC_e4vADTk5J9xBne0q6pbs.TN0n2FjRCayPqLSFuFKG315ByJUhVU6GckfH2Mf_PIk")
	proxyreq.Header.Set("Content-Type", "application/json")
	proxyreq.Header.Set("Accept", "application/json")

	resp, _ := client.Do(proxyreq)

	// Display all elements.
	// for i := range result {
	// 	fmt.Println(result[i])
	// }
	// // Length is 3.
	// fmt.Println(len(result))

	y, _ := ioutil.ReadAll(resp.Body)
	fmt.Printf("\nRESPONSE BODY:\n%v\n\n", string(y))
	fmt.Printf("%v\n", y)

	defer resp.Body.Close()

	var auth Allowed
	// json.NewDecoder(resp.Body).Decode(&auth)
	json.Unmarshal(y, &auth)

	fmt.Printf("ALLOWED: %v\n\n", auth)

	return auth.Allowed
}

func microserviceHandler(w http.ResponseWriter, req *http.Request) {
	// action := c.Param("action")

	fmt.Printf("HOST: %v\n", req.Host)
	fmt.Printf("SCHEME: %v\n", req.Header.Get("X-Forwarded-Proto"))
	fmt.Printf("METHOD: %v\n", req.Method)
	fmt.Printf("URI: %v\n", req.RequestURI)

	// x, _ := ioutil.ReadAll(req.Body)
	cfg := &tls.Config{
		InsecureSkipVerify: true,
	}

	url := fmt.Sprintf("%s://%s%s", req.Header.Get("X-Forwarded-Proto"), req.Host, req.RequestURI)
	fmt.Printf("FULL URL: %v\n\n", url)
	client := &http.Client{}
	client.Transport = &http.Transport{
		TLSClientConfig: cfg,
	}
	// var jsonStr = []byte(x)
	// proxyreq, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonStr))
	// http.NewRequest(method, urlStr, body)
	proxyreq, _ := http.NewRequest("GET", url, nil)
	proxyreq.Header.Set("Content-Type", "application/json")
	proxyreq.Header.Set("Accept", "application/json;v=1")
	proxyreq.Header.Set("Origin", req.Host)
	// proxyreq.Header.Set("Origin", req.Header.Get("X-Forwarded-Proto")+"://"+req.Host)

	resp, _ := client.Do(proxyreq)
	fmt.Printf("%v RESPONSE: %v", req.Host, resp)

}
