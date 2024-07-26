#Asymmetry map
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
asympattern = r'.* \| .* \| .* \| Asymmetry \((.*) um\)'
edge1pattern = r'.* \| .* \| .* \| Edge sensor 1: (.*)'
edge2pattern = r'.* \| .* \| .* \| Edge sensor 2: (.*)'
chipids = []
contactheight = []
asymmetries = []
for i in range(len(log_content)):
    chipmatch = re.search(chippattern, log_content[i])
    contactmatch = re.search(contactpattern, log_content[i])
    waferbatch_match = re.search(waferbatch_pattern, log_content[i])
    waferid_match = re.search(waferid_pattern, log_content[i])
    if chipmatch:
        chipid = str(chipmatch.group(3))
        chipids.append(chipid)
    elif contactmatch:
        contactheight.append(contactmatch.group(3))
        asymmatch = re.search(asympattern, log_content[i-1])
        edge1match = re.search(edge1pattern, log_content[i-8])
        edge2match = re.search(edge2pattern, log_content[i-7])
        if asymmatch and edge1match and edge2match:
            edge1 = str(edge1match.group(1))
            edge2 = str(edge2match.group(1))
            if edge1 == "False" and edge2 == "True":
                asymmetries.append(asymmatch.group(1))
            elif edge1 == "True" and edge2 == "False":
                asymmetries.append(str('-' + asymmatch.group(1)))
            elif (edge1 == "True" and edge2 == "True") or (edge1 == "False" and edge2 == "False"):
                asymmetries.append(asymmatch.group(1))
            else:
                print('edge sensor error')
        else:
            print('no match')
    if waferbatch_match:
        wafer_batch = waferbatch_match.group(1)
    if waferid_match:
        wafer_id = waferid_match.group(1)  
                
#Organize data
asymmetries = [int(i) for i in asymmetries]

    #Format chips (e.g. A9 is (10,9))
chip_coords = [f'({s[0]},{s[1]})' for s in chipids]
letter_to_number = {
    'A': '10', 'B': '11', 'C': '12', 'D': '13', 'E': '14', 'F': '15'}
def multiple_substitutions(s):
    pattern = re.compile('|'.join(map(re.escape, letter_to_number.keys())))
    return pattern.sub(lambda match: letter_to_number[match.group(0)], s)
chiplocations = [multiple_substitutions(s) for s in chip_coords]

#determine status ranges
min_height = int(min(asymmetries))
max_height = int(max(asymmetries))
height_range = max_height - min_height
bin_size = height_range / 4.0

#sort chips into statuses
low = []
medlow = []
med = []
medhigh = []
high = []
other = []
low_c = []
medlow_c = []
med_c = []
medhigh_c = []
high_c = []
other_c = []
for i in range(len(asymmetries)):
    value_asym = asymmetries[i]
    value_chip = chiplocations[i]
    if int(value_asym) <= -4:
        low.append(value_chip)
        low_c.append(value_asym)
    elif int(value_asym) == -2:
        medlow.append(value_chip)
        medlow_c.append(value_asym)
    elif int(value_asym) == 0:
        med.append(value_chip)
        med_c.append(value_asym)
    elif int(value_asym) == 2:
        medhigh.append(value_chip)
        medhigh_c.append(value_asym)
    elif int(value_asym) >= 4:
        high.append(value_chip)
        high_c.append(value_asym)
    else: #just for errors
        other.append(value_chip)
        other_c.append(value_asym)

#find out which chips are at the median, max, and min height
median = np.median(asymmetries)
if median not in asymmetries:
    greater_than_median = [num for num in contactheight if num > median]
    next_highest = min(greater_than_median)
else: next_highest = None
median_chips = []
next_chips = []
max_chips = []
min_chips = []
for i in range(len(asymmetries)):
    if asymmetries[i] == median:
        median_chips.append(chipids[i])
    if asymmetries[i] == next_highest:
        next_chips.append(chipids[i])
    if asymmetries[i] == max_height:
        max_chips.append(chipids[i])
    if asymmetries[i] == min_height:
        min_chips.append(chipids[i])

#make dictionaries
low_dict = {k:v for k,v in zip(low,low_c)}
medlow_dict = {k:v for k,v in zip(medlow,medlow_c)}
med_dict = {k:v for k,v in zip(med,med_c)}
medhigh_dict = {k:v for k,v in zip(medhigh,medhigh_c)}
high_dict = {k:v for k,v in zip(high,high_c)}

#set statuses
chip_statuses = {
		( 1, ''): low_dict,    
		( 2, ''): medlow_dict,                
		( 3, ''): med_dict, 
		( 4, ''): medhigh_dict, 
		( 5, ''): high_dict,              
    }

WaferMap.STATUS_COLORS = {1: '#0099cc', 2: '#669900', 3: '#ffcc00', 4: '#ff9900', 5: '#cc0000'}
WaferMap.STATUS_NAMES =  {1: 'l',       2: 'ml',      3: 'm',       4: 'mh',      5: 'h'}  

#Create map
loop = 0
ch_type ='CROCv2'
wafer_map = WaferMap(chip_type=ch_type, title=f'Wafer {wafer_batch}-{wafer_id} Asymmetry (range: {min_height}um to {max_height}um)')
for (chip_status, chip_value), x in chip_statuses.items():
    for chips,heights in x.items():
        subtext = f"{heights}um"
        wafer_map.set_chip(eval(chips), chip_status, subtext)
        loop = loop + 1

#printing stats
print(f'Range: {min_height}um to {max_height}um ({max_height-min_height}um)')
print(f'Bins:\n - Low (l):          -4um or less\n - Medium low (ml):  2um\n - Medium (m):       0um\n - Medium high (mh): 2um\n - High (h):         4um or higher')
print(f'Mean: {round(np.mean(asymmetries),3)}um')
print(f'Median: {int(np.median(asymmetries))}um')
print(f'Mode: {stats.mode(asymmetries)[0]}um')
if median in asymmetries:
    print(f'Chips at median height({int(median)}um): {", ".join(median_chips)}')
elif median not in asymmetries:
    print(f'Calculated median not in data set. Chips at next highest height ({next_highest}um): {next_chips}')
print(f'Chips at maximum asymmetry ({max_height}um): {", ".join(max_chips)}')
print(f'Chips at minimum asymmetry ({min_height}um): {", ".join(min_chips)}')

#CHANGE OUT PATH
dir = os.path.expanduser('~/Desktop/CMS-Wafer-Testing/Topography-Maps')

#Save map
out_path = os.path.join(dir, f'Asymmetry_map_{wafer_batch}-{wafer_id}.png')
wafer_map.save(out_path)
print(f'+ Saved wafer map: {out_path}')