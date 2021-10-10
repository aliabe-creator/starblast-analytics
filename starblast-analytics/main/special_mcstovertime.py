'''
Created on Oct 9, 2021

@author: Private
'''

#tracks mcst player count over time.

import gspread
import slack
from dotenv import load_dotenv
import os
import time
import requests
from pprint import pprint
from datetime import datetime

load_dotenv()
slack_token = os.environ.get("slack_token")
client = slack.WebClient(token = slack_token)

client.chat_postMessage(channel='C027YMXQM7U', text='e')

gc = gspread.service_account()
sh = gc.open("MCST Playercount over Time - SChickenMan")
sheet = sh.sheet1

def main(timeout = 0):
    total_players = 0
    
    time.sleep(timeout) #if none specified, is 0
    
    try:
        simstatus = requests.get('https://starblast.io/simstatus.json') #get simstatus
        json_status = simstatus.json()
    except Exception as e:  
        client.chat_postMessage(channel='C027YMXQM7U', text=e)
        main(60)
    
    for system in json_status:
        list_modes = system.get('systems')
        
        for m in list_modes:
            if m.get('mod_id') == 'mcst':
                players = m.get('players')
                total_players += players
    
    if total_players == 0: #meaning likely no mcst matches active now
        main(60)
    
    cell = sheet.find("firstblank") #this is put in the first blank cell in the first column
    write_row = cell.row
    
    print('writing')
    
    #write to sheet!
    sheet.update_cell(write_row, 1, str(datetime.now()))
    sheet.update_cell(write_row, 2, str(total_players))
    sheet.update_cell(write_row + 1, 1, 'firstblank')
    
    main(60)
        
main()