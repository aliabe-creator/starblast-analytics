'''
Created on Aug 3, 2021

@author: Private
'''
#ensures that data is actually being added to data.json, as a failsafe.

import slack
from dotenv import load_dotenv
import os
import time
import requests
import json

load_dotenv()

slack_token = os.environ.get("slack_token")

client = slack.WebClient(token = slack_token)
client.chat_postMessage(channel='C027YMXQM7U', text='Analytics Verifier is now online!')

previous_size = 0

while(True):
    filestat = os.stat('data.json')
    byte_size = filestat.st_size
    
    if byte_size == previous_size:
        client.chat_postMessage(channel='C027YMXQM7U', text='Analytics Verifier is now online!')
        
        time.sleep(7200) #waits for 2 hours
    else:
        previous_size = byte_size
        time.sleep(180) #waits for 3 mins