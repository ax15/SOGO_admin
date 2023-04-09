package main

import (
    "io/ioutil"
    "fmt"
    "os"
    "log"
    "encoding/json"
    "net/http"
    "net/url"
    "strconv"
    "time"
)

const ver="v0.50-beta"

type Task struct {
    PerformerID     int       `json:"performerId"`   // id of the user who will work on this task
    Date            string    `json:"datetime"`      // task closing control time (now+2h)?
    Phone           string    `json:"phone"`         // Caller ID
    ExternalPhone   string    `json:"externalPhone"` // our PTSN phone number
    Text            string    `json:"text"`          // task comment "Missed call: +74957777777"
}


var (
    ApiKey            = "9dI3crsLCUaGNmSIOAzGLKjUNGpFJZLo"
    TaskCreate        = "https://vodokomfort.retailcrm.ru/api/v5/tasks/create"
    TeskExecutionTime = time.Hour * 2
    DEBUG             = true
)

func main() {
  log.SetFlags( log.LstdFlags | log.Lshortfile)

  if len(os.Args)<3 {
    log.Fatalf("%s: Wrong list of parameters. Usage example: %s +37257777777 +4951034010 3", ver, os.Args[0])
  } else {
    // TODO: check cli parameters
  }

    dt := time.Now().Add(TeskExecutionTime)
    performer, err := strconv.Atoi(os.Args[3])

    if err!=nil {
      log.Fatalf("%s: Wrong performer id parameter. Should be interger instead of: %s", ver, os.Args[3])
    }

    createTask := &Task{
        Phone: os.Args[1],
        ExternalPhone: os.Args[2],
        PerformerID: performer,
        Date: dt.Format("2006-1-2 15:04"),
        Text: "Missed call: " + os.Args[1] +"!" }

    jsonData, err := json.Marshal( createTask )
    if err != nil {
      log.Fatal(err)
    }

    if DEBUG {
      log.Printf("version      : %s\n", ver)
      log.Printf("OS args count: %v\n", len(os.Args))
      log.Printf("OS args      : %s\n", os.Args)
      log.Printf("API key      : %s\n", ApiKey)
      log.Printf("JSON         : %s\n", string(jsonData))
      log.Printf("Call URL    : %s\n\n", string(TaskCreate))
    }

    jsonUrlData := url.Values{}
    jsonUrlData.Set("apiKey", ApiKey)
    jsonUrlData.Set("task", string(jsonData))

    resp, err := http.PostForm( TaskCreate, jsonUrlData )

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

