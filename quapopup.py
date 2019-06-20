#! /usr/local/bin/python
# coding:utf-8
import requests
import json
import time
import sys

credential = 'apikey/apiid'
headers = {'X-Auth-Token':credential,'Content-Type':'application/json'}
sensorid = sys.argv[1]


def ssession():
    url = "https://api-prod05.conferdeploy.net/integrationServices/v3/cblr/session/%s" % sensorid
    params = {"sensor_id":int(sensorid)}
    global sessionid
    global s
    s = requests.Session()
    req = s.post(url,headers=headers,params=params)
    if req.status_code == 401:
        print "it might be credential is wrong"
        sys.exit(1)
    sessionid = str(req.json()["id"] )
    if req.json()["status"] == "PENDING":
        while True:
            print "status is pending, wait 5 seconds..."
            time.sleep(5)
            req2 = s.get("https://api-prod05.conferdeploy.net/integrationServices/v3/cblr/session/%s" % sessionid,headers=headers)
            if req2.json()["status"] != "PENDING":
                print "session established"
                print json.dumps(req2.json(), indent=4, separators=(',', ': '))
                checkOS(req2.json())
                break
            else:
                print json.dumps(req2.json(), indent=4, separators=(',', ': '))
                continue
    else:
        print "session established"
        checkOS(req.json())
        pass


def checkOS(kwd):
    global os
    if "Windows" in kwd["current_working_directory"]:
        os = "Win"
    elif "MacOS" in kwd["current_working_directory"]:
        os = "Mac"
    else:
        print "might be Linux... Bye"
        closesession()
        sys.exit(1)


def closesession():
    url = "https://api-prod05.conferdeploy.net/integrationServices/v3/cblr/session"
    params = json.dumps({"session_id": "%s" % sessionid, "status": "CLOSE"})
    print "close session"
    req = s.put(url,headers=headers,data=params)
    print json.dumps(req.json(), indent=4, separators=(',', ': '))


def popupmsg():
    if os == "Win":
        msg = "msg * '\xe9\x9a\x94\xe9\x9b\xa2\xe3\x81\x95\xe3\x82\x8c\xe3\x81\xbe\xe3\x81\x97\xe3\x81\x9f'"
    elif os == "Mac":
        msg = "osascript -e 'tell app \"System Events\" to display dialog \"\xe9\x9a\x94\xe9\x9b\xa2\xe3\x81\x95\xe3\x82\x8c\xe3\x81\xbe\xe3\x81\x97\xe3\x81\x9f\"'"
    #msg = "osascript -e 'display notification \"hogehoge\" with title \"Fuga\"'"
    params = json.dumps({"session_id":"%s" % sessionid,"name":"create process", "object": msg})
    url = "https://api-prod05.conferdeploy.net/integrationServices/v3/cblr/session/%s/command" % sessionid
    req = s.post(url,headers=headers,data=params)
    if req.status_code == 200:
        cmdid = req.json()["id"]
        url2 =  "https://api-prod05.conferdeploy.net/integrationServices/v3/cblr/session/%s/command/%s" % (sessionid,cmdid)
        req2 = s.get(url2,headers=headers)
        print json.dumps(req2.json(), indent=4, separators=(',', ': '))
        if req2.json()["status"] == "pending":
            while True:
                time.sleep(5)
                req3 = s.get(url2,headers=headers)
                print json.dumps(req3.json(), indent=4, separators=(',', ': '))
                if req3.json()["status"] == "complete":
                    time.sleep(1)
                    print "finish"
                    closesession()
                    sys.exit(1)
                elif req3.json()["status"] == "error":
                    print "error"
                    time.sleep(10)
                    popupmsg()
                else:
                    pass
                                        
        else:
            time.sleep(1)
            print finish
            closesession()
            sys.exit(1)
    else:
        print "status_code:" + str(req.status_code)
        closesession()
        sys.exit(1)

if __name__ == "__main__":
    ssession()
    popupmsg()


