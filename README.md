Simple tool for pushing events from Asterisk into RCM using commandline

Examples:

*a2event +37257777777 +4951034010*

where:
  - "+37277777777"  - remote caller phone number
  - "+4957777777"   - our called external phone number


*a2upload +37257777777 +4951034010 101 record-id-xxx https://phone-records.vodocomfort.ru/record/record-id-xxx.mp3*

where:
  - "+37257777777"  - remote caller phone number
  - "4957777777"    - our called external phone number
  - "101"           - called extention
  - "record-id-xxx  - uniq call ID in our PBX
  - "https://phone-records.vodocomfort.ru/record/record-id-xxx.mp3"
                    - link where located voice call record

*a2task +37257777777 +4951034010 3*

where:
  - "+37257777777"  - remote caller phone number
  - "4957777777"    - our called external phone number
  - "3"             - user ID who will perform this task
