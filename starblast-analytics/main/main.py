'''
Created on Jul 29, 2021

@author: Private
'''
from bokeh.plotting import figure, show, save
from bokeh.models import Title
import requests
from pprint import pprint
import time
from datetime import datetime
import json

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
        region_time.append(datetime.strptime(d, '%Y-%m-%d %H:%M:%S.%f'))
        
    f.close()

# create a new plot with a title and axis labels
p = figure(title="Players over Time", toolbar_location="above", plot_width=1000, plot_height=600, x_axis_label='Time', x_axis_type = 'datetime', y_axis_label='Number of active players')

#add plot description
p.add_layout(Title(text="Click on legend labels to hide/show plots. Data is constantly updated.", align="left"), "below")

# add a line renderer with legend and line thickness to the plot
p.line(total_time, total_count, legend_label="Total Players", line_width=2, color = 'blue')
p.line(region_time, america_count, legend_label="America Players", line_width=2, color = 'red')
p.line(region_time, asia_count, legend_label="Asia Players", line_width=2, color = 'green')
p.line(region_time, europe_count, legend_label="Europe Players", line_width=2, color = 'purple')

p.title.text_font_size = "25px"
p.title.align = "left"
p.title.text_color = "black"
p.legend.location = "top_left"
p.legend.click_policy="hide"

while(True):
    simstatus = requests.get('https://starblast.io/simstatus.json')
    json_status = simstatus.json()
    
    tot = 0
    amer = 0
    asi = 0
    eu = 0
    
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
    
    total_time.append(datetime.now()) #updating bokeh plot
    region_time.append(datetime.now())
    
    total_count.append(tot)
    america_count.append(amer)
    asia_count.append(asi)
    europe_count.append(eu)
    
    data['total']['count'] = total_count #reset count to y array contents
    data['region']['america'] = america_count
    data['region']['asia'] = asia_count
    data['region']['europe'] = europe_count
    
    append_time_tot = []
    append_time_region = []
    
    for a in total_time: #bc cannot save datetime object to file, have to string it
        append_time_tot.append(str(a))
    for b in region_time: #bc cannot save datetime object to file, have to string it
        append_time_region.append(str(b))
    
    data['total']['time'] = append_time_tot #reset time to append_x contents
    data['region']['time'] = append_time_region
    
    with open('data.json', 'w') as f: #dump the new data stuff to json
        json.dump(data, f)
        f.close()
    
    # show the results
    save(p, 'index.html')
    print('done')
    
    time.sleep(5)