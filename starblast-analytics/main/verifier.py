'''
Created on Aug 3, 2021

@author: Private
'''
#ensures that data is actually being added to data.json, as a failsafe.

import os
import time
from dotenv import load_dotenv
import requests
import json

load_dotenv()

signalkey = os.environ.get("signalkey") #OneSignal api key
appid = os.environ.get("appid") #OneSignal app id

header = {"Content-Type": "application/json; charset=utf-8",
          "Authorization": signalkey}

previous_size = 0

while(True):
    filestat = os.stat('data.json')
    byte_size = filestat.st_size
    
    if byte_size == previous_size:
        #Use OneSignal to push message to Android device
        
        payload = {"app_id": appid,
           "included_segments": ["Subscribed Users"],
           "headings": {"en": "Starblast Analytics Notifications"},
           "contents": {"en": "Data file size has not changed in past 3 minutes. Program likely crashed."},
           "priority": 10, #set priority to high
           "android_accent_color": "FFFF0000"}
        
        requests.post("https://onesignal.com/api/v1/notifications", headers=header, data=json.dumps(payload))
        
        break
    else:
        previous_size = byte_size
        time.sleep(180) #waits for 3 mins