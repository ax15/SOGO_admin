package vars

import "time"

var (

    ApiKey          = "9dI3crsLCUaGNmSIOAzGLKjUNGpFJZLo"
    CallEventURL    = "https://vodokomfort.retailcrm.ru/api/v5/telephony/call/event"
    CallUpload      = "https://vodokomfort.retailcrm.ru/api/v5/telephony/calls/upload"
    TaskCreate      = "https://vodokomfort.retailcrm.ru/api/v5/tasks/create"
    EventCodeGroup  = []string{ "101","102" }
    DEBUG           = true

    TeskExecutionTime = time.Hour * 2

    //LogFile         = "/var/log/asterisk/crm.log"
    LogFile         = "crm.log"

)
