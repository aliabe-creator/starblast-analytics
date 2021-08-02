'''
Created on Jul 29, 2021

@author: Private
'''
from bokeh.plotting import figure, save
from bokeh.models import Title, HoverTool
from bokeh.layouts import column
import requests
import time
from datetime import datetime
import json
from bokeh.io.output import reset_output
import boto3
from dotenv import load_dotenv
import os

error_sent = False #so only send error email once via SNS

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

with open('data.json', 'r') as f: #only need to do at beginning
    data = json.load(f)
    
    total_count = data.get('total').get('count') #get total statistics
    total_time = []
        
    for d in data.get('total').get('time'):
        total_time.append(datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f'))
    
    america_count = data.get('region').get('america') #get region counts
    asia_count = data.get('region').get('asia')
    europe_count = data.get('region').get('europe')
    region_time = []
    
    for e in data.get('region').get('time'):
        region_time.append(datetime.strptime(e, '%Y-%m-%d %H:%M:%S.%f'))
        
    team_count = data.get('mode').get('team') #get mode counts
    survival_count = data.get('mode').get('survival')
    pdm_count = data.get('mode').get('pdm')
    invasion_count = data.get('mode').get('invasion')
    mode_time = []
    
    for g in data.get('mode').get('time'):
        mode_time.append(datetime.strptime(g, '%Y-%m-%d %H:%M:%S.%f'))
    
    f.close()

def yes():
    global error_sent
    
    try:
        simstatus = requests.get('https://starblast.io/simstatus.json') #get simstatus
        json_status = simstatus.json()
    except Exception as e:  
        if error_sent == False:
            sns.publish(TopicArn=topics[0]['TopicArn'], 
                        Message=e, 
                        Subject="Error fetching simstatus.")
            error_sent = True
            
        time.sleep(30)
        yes()
    
    # create a new plot with a title and axis labels
    p = figure(title="Players over Time", toolbar_location="above", plot_width=1000, plot_height=600, x_axis_label='Time', x_axis_type = 'datetime', y_axis_label='Number of players')
    
    # add a line renderer with legend and line thickness to the plot
    p.line(total_time, total_count, legend_label="Total Players", line_width=2, color = 'blue')
    p.line(region_time, america_count, legend_label="America Players", line_width=2, color = 'red')
    p.line(region_time, asia_count, legend_label="Asia Players", line_width=2, color = 'green')
    p.line(region_time, europe_count, legend_label="Europe Players", line_width=2, color = 'purple')
    
    p.add_tools(HoverTool( #format hover tool
        tooltips=[
            ('date', '$x{%F %H:%M}'),
            ('player count', '$y{0.}')
        ],
    
        formatters={
            '$x': 'datetime' # use 'datetime' formatter for '@date' field
        },
    ))
    
    #add plot description
    p.add_layout(Title(text="Click on legend labels to hide/show plots. Data is constantly updated.", align="left"), "right")
    
    #some formatting
    p.title.text_font_size = "25px"
    p.title.align = "left"
    p.title.text_color = "black"
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    
    #second graph
    q = figure(title="Players over Time by Mode", toolbar_location="above", plot_width=1000, plot_height=600, x_axis_label='Time', x_axis_type = 'datetime', y_axis_label='Number of players')
    q.add_layout(Title(text="Click on legend labels to hide/show plots. Data is constantly updated.", align="left"), "right")
    
    q.line(mode_time, team_count, legend_label="Team", line_width=2, color = 'lime')
    q.line(mode_time, survival_count, legend_label="Survival", line_width=2, color = 'tomato')
    q.line(mode_time, pdm_count, legend_label="Pro Deathmatch", line_width=2, color = 'firebrick')
    q.line(mode_time, invasion_count, legend_label="Invasion", line_width=2, color = 'purple')
    
    q.add_tools(HoverTool( #add hover tooltip
        tooltips=[
            ('date', '$x{%F %H:%M}'),
            ('player count', '$y{0.}')
        ],
    
        formatters={
            '$x': 'datetime' # use 'datetime' formatter for '@date' field
        },
    ))
    
    #some formatting
    q.title.text_font_size = "25px"
    q.title.align = "left"
    q.title.text_color = "black"
    q.legend.location = "top_left"
    q.legend.click_policy="hide"
    
    #set counter values
    tot = 0
    amer = 0
    asi = 0
    eu = 0
    team = 0
    survival = 0
    pdm = 0
    invasion = 0
    
    for system in json_status:
        players = system.get('current_players')
        tot = tot + players
        
        #region by region sums
        if system.get('location') == 'America':
            amer = amer + players
        if system.get('location') == 'Asia':
            asi = asi + players
        if system.get('location') == 'Europe':
            eu = eu + players
            
        list_modes = system.get('systems')
        
        for m in list_modes:
            if m.get('mode') == 'team':
                team = team + m.get('players')
            if m.get('mode') == 'survival':
                survival = survival + m.get('players')
            if m.get('mode') == 'deathmatch':
                pdm = pdm + m.get('players')
            if m.get('mode') == 'invasion':
                invasion = invasion + m.get('players')
                
    total_time.append(datetime.now()) #updating bokeh plot
    region_time.append(datetime.now())
    mode_time.append(datetime.now())
    
    total_count.append(tot)
    america_count.append(amer)
    asia_count.append(asi)
    europe_count.append(eu)
    team_count.append(team)
    survival_count.append(survival)
    pdm_count.append(pdm)
    invasion_count.append(invasion)
    
    data['total']['count'] = total_count #reset count to y array contents
    data['region']['america'] = america_count
    data['region']['asia'] = asia_count
    data['region']['europe'] = europe_count
    data['mode']['team'] = team_count
    data['mode']['survival'] = survival_count
    data['mode']['pdm'] = pdm_count
    data['mode']['invasion'] = invasion_count
    
    append_time_tot = []
    append_time_region = []
    append_time_mode = []
    
    for a in total_time: #bc cannot save datetime object to file, have to string it
        append_time_tot.append(str(a))
    for b in region_time:
        append_time_region.append(str(b))
    for c in mode_time:
        append_time_mode.append(str(c))
    
    data['total']['time'] = append_time_tot #reset time to append_x contents
    data['region']['time'] = append_time_region
    data['mode']['time'] = append_time_mode
    
    with open('data.json', 'w') as f: #dump the new data stuff to json
        json.dump(data, f)
        f.close()
    
    # save the results
    reset_output()
    save(column(p, q), filename = 'index.html', title = 'Starblast.io Activity Archive Project')
    print('done')
    
    time.sleep(45)
    yes() #recall. This avoids problems with assignment of p and q.
    
yes()
    
