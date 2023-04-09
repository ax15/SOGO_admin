package main

import (
    "io/ioutil"
    "fmt"
    "os"
    "log"
    "encoding/json"
    "net/http"
    "net/url"
)

const ver="v0.46-beta"

type Event struct {
    Phone           string   `json:"phone"`   // Caller ID
    Type            string   `json:"type"`    // Type may be one of the next options: hangup|in|out
    Codes           []string `json:"codes"`   // Extentions
    ExternalPhone   string   `json:"externalPhone"`    // Our PTSN phone number where we got incoming call
}


var (
    ApiKey          = "9dI3crsLCUaGNmSIOAzGLKjUNGpFJZLo"
    CallEventURL    = "https://vodokomfort.retailcrm.ru/api/v5/telephony/call/event"
    CodeGroup       = []string{ "101","102" }
    DEBUG           = false
)

func main() {
  log.SetFlags( log.LstdFlags | log.Lshortfile)

  if len(os.Args)<3 {
    log.Fatalf("%s: Wrong list of parameters. Usage example: %s +37257777777 +4951034010", ver, os.Args[0])
  } else {
    // TODO: check cli parameters
  }
    evnt := &Event{
      Phone: os.Args[1],
      Type: "in",                       // hardcoded by MNZ request 2023.04.09
      Codes: CodeGroup,                 // hardcoded by MNZ request 2023.04.09
      ExternalPhone: os.Args[2]}

    jsonData, err := json.Marshal(evnt)
    if err != nil {
      log.Fatal(err)
    }

    if DEBUG {
      log.Printf("version      : %s\n", ver)
      log.Printf("OS args count: %v\n", len(os.Args))
      log.Printf("OS args      : %s\n", os.Args)
      log.Printf("API key      : %s\n", ApiKey)
      log.Printf("JSON         : %s\n", string(jsonData))
      log.Printf("Event URL    : %s\n\n", string(CallEventURL))
    }

    jsonUrlData := url.Values{}
    jsonUrlData.Set("apiKey", ApiKey)
    jsonUrlData.Set("event", string(jsonData))

    resp, err := http.PostForm( CallEventURL, jsonUrlData )

    if err !=nil {
      log.Println(err)
    } else {
      log.Printf("HTTP response: %d\n", resp.StatusCode)

      body, _ := ioutil.ReadAll(resp.Body)
      defer resp.Body.Close()

      if resp.StatusCode == 400 {
          fmt.Printf("%s\n", body)
      }

    }

}

