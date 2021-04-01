# fz44-etp-test 
# Platform for 44fz

## USAGE

**usage:** 
```
fz44-platform.py [-h] [--web] [--url [URL]] [--delay [DELAY]]
                        [--debug [DEBUG]] [--timeout [TIMEOUT]] [--n [N]]
```

**optional arguments:**

  -h, --help - show this help message and exit
  
  --web - start http web service, default disable
  
  --url [URL] - http address common-api-cft-etp service, default "http://127.0.0.1:8080/etp"
  
  --delay [DELAY] - delay between requests, default 1 minute 
  
  --debug [DEBUG] - debug level [0, 1], default 0
  
  --timeout [TIMEOUT] - response timeout, default 30 minutes
  
  --n [N] - generating N requests without timeout, default disable

## EXAMPLES

```./fz44-platform.py --web --url http://stunnel:1500/etp --delay 5 --debug 1 --timeout 60 ```

```./fz44-platform.py --n 10000 --url http://common-api-cft-etp:8080/etp --timeount 120 ```

## DOCKER

```docker build -t <image_name> .```

```docker run -p 80:8080 -d --name fz44-etp-test --restart always --env FZ44_URL=<etp_url>
                 --env FZ44_DELAY=5 --env FZ44_TIMEOUT=30 
                 -p <port>:8080 --env PYTHONUNBUFFERED=1 <image_name>```

## WEB SERVER URLs

/status - show service status
/cft-etp - xml-files reception 
/print_queue - show requests without response
/print_requests - show requests with response, debug level 1
/remove?id=<id> - remove request from queue (GET method)
/send - send XML-file (POST method) 
