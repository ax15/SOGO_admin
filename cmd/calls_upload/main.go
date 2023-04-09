package main

import (
    "io/ioutil"
    "fmt"
    "os"
    "log"
    "encoding/json"
    "net/http"
    "net/url"
    "time"
)

const ver="v0.49-beta"

type Call struct {
    Date            string    `json:"date"`          // Call date and time
    Phone           string    `json:"phone"`         // Caller ID
    Type            string    `json:"type"`          // Type may be one of the next options: hangup|in|out
    Code            string    `json:"code"`          // Who received a call (extention)
    Result          string    `json:"result"`        // answered|busy|failed|no answer|not allowed|unknown
    ExternalPhone   string    `json:"externalPhone"` // our PTSN phone number
    ExternalID      string    `json:"externalId"`    // Call ID in PBX (date+time?)
    RecordURL       string    `json:"recordUrl"`     // direct link to the saved call record
}

type Calls struct {
    Calls           []Call    `json:"calls"`        // array of calls records
}

var (
    ApiKey          = "9dI3crsLCUaGNmSIOAzGLKjUNGpFJZLo"
    CallUpload      = "https://vodokomfort.retailcrm.ru/api/v5/telephony/calls/upload"
    DEBUG           = true
)

func main() {
  log.SetFlags( log.LstdFlags | log.Lshortfile)

  if len(os.Args)<3 {
    log.Fatalf("%s: Wrong list of parameters. Usage example: %s +37257777777 +4951034010 101 record-id-xxx https://phone-records.vodocomfort.ru/record/record-id-xxx.mp3", ver, os.Args[0])
  } else {
    // TODO: check cli parameters
  }

    recordCall := &Call{
        Phone: os.Args[1],
        Type: "in",                       // hardcoded by MNZ request
        ExternalPhone: os.Args[2],
        Code: os.Args[3],
        Result: "answered",
        Date: time.Now().Format("2006-1-2 15:04:05"),
        ExternalID: os.Args[4],
        RecordURL: os.Args[5] }

   var uploadCalls [1]Call
   uploadCalls[0] = *recordCall

    jsonData, err := json.Marshal(uploadCalls)
    if err != nil {
      log.Fatal(err)
    }

    if DEBUG {
      log.Printf("version      : %s\n", ver)
      log.Printf("OS args count: %v\n", len(os.Args))
      log.Printf("OS args      : %s\n", os.Args)
      log.Printf("API key      : %s\n", ApiKey)
      log.Printf("JSON         : %s\n", string(jsonData))
      log.Printf("Call URL    : %s\n\n", string(CallUpload))
    }

    jsonUrlData := url.Values{}
    jsonUrlData.Set("apiKey", ApiKey)
    jsonUrlData.Set("calls", string(jsonData))

    resp, err := http.PostForm( CallUpload, jsonUrlData )

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

