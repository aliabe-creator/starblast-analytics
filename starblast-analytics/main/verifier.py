'''
Created on Aug 3, 2021

@author: Private
'''
#ensures that data is actually being added to data.json, as a failsafe.

import os
import time
import boto3
from dotenv import load_dotenv

load_dotenv()

keyid = os.environ.get("keyid")
secret = os.environ.get("secret")

# Create an SNS client
sns = boto3.client(
    "sns",
    region_name="us-east-1", 
    aws_access_key_id=keyid, 
    aws_secret_access_key=secret
)

response = sns.list_topics()
topics = response["Topics"] #get array of SNS Topics

previous_size = 0

while(True):
    filestat = os.stat('data.json')
    byte_size = filestat.st_size
    
    if byte_size == previous_size:
        sns.publish(TopicArn=topics[0]['TopicArn'], 
                        Message="Program is likely stopped, data file size has not increased in the past 3 minutes.", 
                        Subject="Starblast Analytics: Stop Warning")
        break
    else:
        previous_size = byte_size
        time.sleep(180) #waits for 3 mins