'''
Created on Jul 29, 2021

@author: Private
'''
#important change: python now actually has a recursion limit, so this program is just called by a .exp program externally.
#if you want to run this program, you must change the paths to the files as necessary, and create your own site that embeds bokeh.html

from bokeh.plotting import figure, save
from bokeh.models import Title, HoverTool, DatetimeTickFormatter
from bokeh.layouts import column, row
import requests
import time
from datetime import datetime
import json
from bokeh.io.output import reset_output
from dotenv import load_dotenv
import os
import psutil
import sys
from bokeh.models.tickers import AdaptiveTicker
from bs4 import BeautifulSoup as bs
import matplotlib.pyplot as plt
from math import pi
import slack

load_dotenv()

slack_token = os.environ.get("slack_token")

client = slack.WebClient(token = slack_token)

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
    
    useries_count = data.get('mod').get('useries')
    mcst_count = data.get('mod').get('mcst')
    nautic_count = data.get('mod').get('nauticseries')
    rumble_count = data.get('mod').get('rumble')
    br_count = data.get('mod').get('battleroyale')
    ai_count = data.get('mod').get('alienintrusion')
    src_count = data.get('mod').get('src2')
    dtm_count = data.get('mod').get('dtm')
    sdc_count = data.get('mod').get('sdc')
    ctf_count = data.get('mod').get('ctf')
    
    f.close()

def editBokeh():
    html = open('bokeh.html') #open html
    soup = bs(html, 'html.parser') #parse html
    divtocenter = soup.find('div', {'class': 'bk-root'}) #store div tag
    
    divtocenter['align'] = 'center' #aligns bokeh plots to center to ensure iframe embed also in center
    
    with open('bokeh.html', 'wb') as f_output: #writes changes
        f_output.write(soup.prettify('utf-8'))
        
    return

def editOverview(total_players, record_players, mod_array):
    html = open('index.html')
    soup = bs(html, 'html.parser') #parse html
    
    #first add currently online players
    total_online = soup.find('p', {'class': 'online'}) #store div tag
    nt = soup.new_tag('ins') #use tag replace instead of append to ensure that number will fully change
    nt.string = str(total_players)
    total_online.ins.replace_with(nt)
    
    #next update record players
    record = soup.find('p', {'class': 'record'})
    nt = soup.new_tag('ins')
    nt.string = str(record_players)
    record.ins.replace_with(nt)
    
    #next update favorite mod
    #find most popular mod
    
    mod_dict = {}
    
    mod_dict['U-Series'] = mod_array[0]
    mod_dict['MCST'] = mod_array[1]
    mod_dict['Nautic-Series'] = mod_array[2]
    mod_dict['Rumble'] = mod_array[3]
    mod_dict['Battle Royale'] = mod_array[4]
    mod_dict['Alien Intrusion'] = mod_array[5]
    mod_dict['SRC'] = mod_array[6]
    mod_dict['DTM'] = mod_array[7]
    mod_dict['SDC'] = mod_array[8]
    mod_dict['CTF'] = mod_array[9]
    
    max_key = max(mod_dict, key=mod_dict.get) #find key with max value

    fm = soup.find('p', {'class': 'modpop'})
    nt = soup.new_tag('ins')
    nt.string = max_key
    fm.ins.replace_with(nt)
    
    with open('index.html', 'wb') as f_output:
        f_output.write(soup.prettify('utf-8'))
        
    return

def yes():
    global error_sent
    global data
    global total_count
    global total_time
    global america_count
    global asia_count
    global europe_count
    global region_time
    global team_count
    global survival_count
    global pdm_count
    global invasion_count
    global mode_time
    global useries_count
    global mcst_count
    global nautic_count
    global rumble_count
    global br_count
    global ai_count
    global src_count
    global dtm_count
    global sdc_count
    global ctf_count
    
    try:
        simstatus = requests.get('https://starblast.io/simstatus.json') #get simstatus
        json_status = simstatus.json()
    except Exception as e:  
        client.chat_postMessage(channel='C027YMXQM7U', text=e)
            
        time.sleep(60)
        yes()
    
    # create a new plot with a title and axis labels
    p = figure(title="Players over Time", tools="pan, zoom_in, zoom_out, box_zoom, undo, redo, reset, save", toolbar_location="above", plot_width=900, plot_height=400, x_axis_label='Time', x_axis_type = 'datetime', y_axis_label='Number of players')
    
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
    p.add_layout(Title(text="Click on legend labels to hide/show plots.", align="left"), "right")
    
    #some formatting
    p.title.text_font_size = "20px"
    p.title.align = "left"
    p.title.text_color = "royalblue"
    p.legend.location = "top_left"
    p.legend.click_policy="hide"
    
    p.xaxis[0].ticker = AdaptiveTicker(desired_num_ticks=12)
    
    #Below fixes datetime stuff on x-axis
    p.xaxis.formatter = DatetimeTickFormatter(
        days=["%m/%d %H:%M"],
        months=["%m/%d %H:%M"],
        hours=["%m/%d %H:%M"],
        minutes=["%m/%d %H:%M"]
    )
    p.xaxis.major_label_orientation = pi/4
    
    #second graph
    q = figure(title="Players over Time by Mode", tools="pan, zoom_in, zoom_out, box_zoom, undo, redo, reset, save", toolbar_location="above", plot_width=900, plot_height=400, x_axis_label='Time', x_axis_type = 'datetime', y_axis_label='Number of players')
    q.add_layout(Title(text="Click on legend labels to hide/show plots.", align="left"), "right")
    
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
    q.title.text_font_size = "20px"
    q.title.align = "left"
    q.title.text_color = "royalblue"
    q.legend.location = "top_left"
    q.legend.click_policy="hide"
    
    q.xaxis[0].ticker = AdaptiveTicker(desired_num_ticks=12)
    
    #Below fixes datetime stuff on x-axis
    q.xaxis.formatter = DatetimeTickFormatter(
        days=["%m/%d %H:%M"],
        months=["%m/%d %H:%M"],
        hours=["%m/%d %H:%M"],
        minutes=["%m/%d %H:%M"]
    )
    q.xaxis.major_label_orientation = pi/4
    
    #Create pie chart for mod popularity tracking
    labels = ['U-Series', 'MCST', 'Nautic-Series', 'Rumble', 'Battle Royale', 'Alien Intrusion', 'SRC', 'DTM', 'SDC', 'CTF']
    mod_data = [useries_count, mcst_count, nautic_count, rumble_count, br_count, ai_count, src_count, dtm_count, sdc_count, ctf_count]
    
    colors = ['#FF1744', '#D500F9', '#546E7A', '#3D5AFE', '#ADFF2F', '#00E676', '#FFC400', '#DF00FF', '#FF7F7F', '#42F5DD']
    explode = (0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05, 0.05)
    
    plt.pie(mod_data, colors=colors, labels=labels, autopct='%1.1f%%', pctdistance=0.75, explode=explode)
    centre_circle = plt.Circle((0, 0), 0.60, fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    
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
            
            #If the mod present in simstatus, increment global var
            if m.get('mod_id') == 'useries':
                useries_count = useries_count + m.get('players')
            if m.get('mod_id') == 'mcst':
                mcst_count = mcst_count + m.get('players')
            if m.get('mod_id') == 'nauticseries':
                nautic_count = nautic_count + m.get('players')
            if m.get('mod_id') == 'rumble':
                rumble_count = rumble_count + m.get('players')
            if m.get('mod_id') == 'battleroyale':
                br_count = br_count + m.get('players')
            if m.get('mod_id') == 'alienintrusion':
                ai_count = ai_count + m.get('players')
            if m.get('mod_id') == 'src2':
                src_count = src_count + m.get('players')
            if m.get('mod_id') == 'dtm':
                dtm_count = dtm_count + m.get('players')
            if m.get('mod_id') == 'sdc':
                sdc_count = sdc_count + m.get('players')
            if m.get('mod_id') == 'ctf':
                ctf_count = ctf_count + m.get('players')
                        
    if (tot == 0 or amer == 0 or asi == 0 or eu == 0): #means that the server is being weird, so exit the program and don't add anything to data.json
        sys.exit()   
             
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
    data['mod']['useries'] = useries_count #overwrite mod overall counts
    data['mod']['mcst'] = mcst_count
    data['mod']['nauticseries'] = nautic_count
    data['mod']['rumble'] = rumble_count
    data['mod']['battleroyale'] = br_count
    data['mod']['alienintrusion'] = ai_count
    data['mod']['src2'] = src_count
    data['mod']['dtm'] = dtm_count
    data['mod']['sdc'] = sdc_count
    data['mod']['ctf'] = ctf_count
    
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
    save(column(p, q), filename = 'bokeh.html', title = 'Starblast.io Activity Archive Project') #save bokeh
    plt.savefig('images/modpie.png', bbox_inches='tight') #save mod pie matplotlib
    editBokeh() #pass to BeautifulSoup for edits
    editOverview(tot, max(total_count), mod_data)
    print('done')

    if (psutil.virtual_memory().percent > 90): #to stop server crashing due to use of memory
        client.chat_postMessage(channel='C027YMXQM7U', text='Server very high memory use, terminating Analytics.')
        
        sys.exit() #quits the program

yes()