#Topography map python
import os
import sys
import re
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker
from wlt.duts.wafers import WAFER_MAPS
from wlt.wafermap import WaferMap
        
#Check sys args
if len(sys.argv) == 2:
    file_path = sys.argv[1]
else:
    print(f"Error: please provide a valid number of command-line arguments")
    sys.exit(1)

if not os.path.isfile(file_path):
    print(f"Error: '{file_path}' is not a valid file path.")
    sys.exit(1)

#Open file
try:
    with open(file_path, 'r') as file:
        log_content = file.readlines()
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
except IOError as e:
    print(f"Error: {e}")

#Set up patterns
waferbatch_pattern = r'.*Batch: (.*)'
waferid_pattern = r'.*Wafer: (.*)'
wafer_batch = ''
wafer_id = ''
chippattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| WaferTester \((\S\S\S\S)\)   \| INFO     \| Testing chip \S\S\S\S\S\S\S\S\S\S\S\S(\S\S)'
contactpattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| WaferTester \((\S\S\S\S)\)   \| INFO     \| Found contact height: (.*)'
chipids = []
contactheight = []
for line in log_content:
    chipmatch = re.search(chippattern, line)
    contactmatch = re.search(contactpattern, line)
    waferbatch_match = re.search(waferbatch_pattern, line)
    waferid_match = re.search(waferid_pattern, line)
    if waferbatch_match:
        wafer_batch = waferbatch_match.group(1)
    if waferid_match:
        wafer_id = waferid_match.group(1)
    if chipmatch:
        chipid = str(chipmatch.group(3))
        chipids.append(chipid)
    if contactmatch:
        contactheight.append(contactmatch.group(3))
                             
#Organize data
contactheight = [int(i[:5]) for i in contactheight]

#Format chips (e.g. A9 is (10,9))
chip_coords = [f'({s[0]},{s[1]})' for s in chipids]
letter_to_number = {
    'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14', 'F': '15'}
def multiple_substitutions(s):
    pattern = re.compile('|'.join(map(re.escape, letter_to_number.keys())))
    return pattern.sub(lambda match: letter_to_number[match.group(0)], s)
chiplocations = [multiple_substitutions(s) for s in chip_coords]

#determine status ranges
min_height = min(contactheight)
max_height = max(contactheight)
height_range = max_height - min_height
bin_size = height_range / 4.0

#sort chips into statuses
low = []
medlow = []
medhigh = []
high = []
low_c = []
medlow_c = []
medhigh_c = []
high_c = []
for i in range(len(contactheight)):
    value_height = contactheight[i]
    value_chip = chiplocations[i]
    if value_height < min_height + bin_size:
        low.append(value_chip)
        low_c.append(value_height)
    elif value_height < min_height + 2 * bin_size:
        medlow.append(value_chip)
        medlow_c.append(value_height)
    elif value_height < min_height + 3 * bin_size:
        medhigh.append(value_chip)
        medhigh_c.append(value_height)
    else:
        high.append(value_chip)
        high_c.append(value_height)

#find out which chips are at the median, max, and min height
median = np.median(contactheight)
if median not in contactheight:
    greater_than_median = [num for num in contactheight if num > median]
    next_highest = min(greater_than_median)
    '''number of chips at next highest value above median'''
else: next_highest = None
median_chips = []
next_chips = []
max_chips = []
min_chips = []
for i in range(len(contactheight)):
    if contactheight[i] == median:
        median_chips.append(chipids[i])
    if contactheight[i] == next_highest:
        next_chips.append(chipids[i])
    if contactheight[i] == max_height:
        max_chips.append(chipids[i])
    if contactheight[i] == min_height:
        min_chips.append(chipids[i])

#make dictionaries
low_dict = {k:v for k,v in zip(low,low_c)}
medlow_dict = {k:v for k,v in zip(medlow,medlow_c)}
medhigh_dict = {k:v for k,v in zip(medhigh,medhigh_c)}
high_dict = {k:v for k,v in zip(high,high_c)}


#set statuses
chip_statuses = {
		( 1, ''): low_dict,    
		( 2, ''): medlow_dict,                
		( 3, ''): medhigh_dict, 
		( 4, ''): high_dict,              
    }

WaferMap.DATA_DIR = os.path.expanduser('~/Desktop/CMS-Wafer-Testing/Topography-Maps')
WaferMap.STATUS_COLORS = {1: '#A5EFFE', 2: '#71d5ea', 3: '#1aa1bc', 4: '#067991'}
WaferMap.STATUS_NAMES =  {1: 'l',       2: 'ml',       3: 'mh',       4: 'h'}


#Create map
loop = 0
ch_type ='CROCv2'
wafer_map = WaferMap(chip_type=ch_type, title=f'Wafer {wafer_batch}-{wafer_id} Contact Height (range: {min_height}um to {max_height}um)')
for (chip_status, chip_value), x in chip_statuses.items():
    for chips,heights in x.items():
        subtext = f"{heights}um"
        wafer_map.set_chip(eval(chips), chip_status, subtext)
        loop = loop + 1
    
#printing stats
print(f'Range: {min_height}um to {max_height}um ({max_height-min_height}um)')
print(f'Bins:\n - Low (l):          {min_height}-{int(min_height+bin_size)}um\n - Medium low (ml):  {int(min_height+bin_size)}-{int(min_height+bin_size*2)}um\n - Medium high (mh): {int(min_height+bin_size*2)}-{int(min_height+bin_size*3)}um\n - High (h):         {int(min_height+bin_size*3)}-{int(max_height)}um')
print(f'Mean: {round(np.mean(contactheight),3)}um')
print(f'Median: {int(np.median(contactheight))}um')
print(f'Mode: {stats.mode(contactheight)[0]}um')
if median in contactheight:
    print(f'Chips at median height: {", ".join(median_chips)}')
elif median not in contactheight:
    print(f'Calculated median not in data set. Chips at next highest height ({next_highest}um): {next_chips}')
print(f'Chips at maximum height: {", ".join(max_chips)}')
print(f'Chips at minimum height: {", ".join(min_chips)}')

#CHANGE OUT PATH
dir = os.path.expanduser('~/Desktop/CMS-Wafer-Testing/Topography-Maps')

#Save map
out_path = os.path.join(dir, f'Topography_map_{wafer_batch}-{wafer_id}.png')
wafer_map.save(out_path)
print(f'+ Saved wafer map: {out_path}')