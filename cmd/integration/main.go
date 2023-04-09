package integration

import (
//    "bytes"
    "fmt"
    "log"
    "io/ioutil"
    "net/http"
    "net/url"
)

const ver="v0.43-beta"

type Event struct {
    Phone           string   `json:"phone"`   // Caller ID
    Type            string   `json:"type"`    // Type may be one of the next options: hangup|in|out
    Codes           []string `json:"codes"`   // Extentions
    ExternalPhone   string   `json:"externalPhone"`    // Our PTSN phone number where we got incoming call
}


var (
    ApiKey          = "9dI3crsLCUaGNmSIOAzGLKjUNGpFJZLo"
    CallEventURL    = "https://subdomain.retailcrm.ru/api/v5/telephony/call/event"
    TasksCreateURL  = "https://subdomain.retailcrm.ru/api/v5/tasks/create"
    IntegrationURL  = "https://vodokomfort.retailcrm.ru/api/v5/integration-modules/new-grundfos/edit"
    integrationJSON = `{
    "code": "new-grundfos",
    "active": true,
    "name": "new-grundfos",
    "logo": "http://api.telephony-test.ru/logo.svg",
    "clientId": "9dI3crsLCUaGNmSIOAzGLKjUNGpFJZLo",
    "accountUrl": "http://api.telephony-test.ru/settings",
    "integrations": {
        "telephony": {
            "makeCallUrl": "http://api.telephony-test.ru/make-call",
            "allowEdit": true,
            "inputEventSupported": true,
            "additionalCodes":[
                {"userId":"101", "code":101},
                {"userId":"102", "code":102}
            ],
            "externalPhones":[
                {"siteCode":"new-grundfos", "externalPhone": "+7-495-103-40-10"}
            ],
            "changeUserStatusUrl": "http://api.telephony-test.ru/change-status"
        }
    }
}`

)

func main() {

    log.Printf("API key            : %s\n", ApiKey)
    log.Printf("JSON               : %s\n", string(integrationJSON))
    log.Printf("Integration URL    : %s\n\n", IntegrationURL)

    jsonUrlData := url.Values{}
    jsonUrlData.Set("apiKey", ApiKey)
    jsonUrlData.Set("integrationModule", string(integrationJSON))

    resp, err := http.PostForm( IntegrationURL, jsonUrlData )
    if err !=nil {
      log.Println(err)
    } else {
      fmt.Printf("HTTP response: %d\n", resp.StatusCode)
      body, _ := ioutil.ReadAll(resp.Body)
      defer resp.Body.Close()
      if resp.StatusCode == 400 {
          fmt.Printf("%s", body)
      }
    }

}

