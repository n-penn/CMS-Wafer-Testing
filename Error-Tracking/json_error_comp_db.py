#gets all failure reasons
#using indiv. chip json files (db folder)
import re
import os
import json
import glob
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from collections import Counter

#open file
folders = ['~/WLT/WLT_v1.2.1/croc_wlt/data/wafer_NC0W14-05*/2024*/plots/db/', '~/WLT/WLT_v1.2.1/croc_wlt/data/Desktop/wafer_NC0W14-07*/2024*/plots/db/']
pattern = r'chip_(.*).json'
errors = []
for folder in folders: 
    expanded_folder = os.path.expanduser(folder)
    matching_directories = glob.glob(expanded_folder)

    # Iterate over matching directories
    for directory in matching_directories:
        # List files in each matching directory
        files = os.listdir(directory)
        
        # Iterate over files in the directory
        for filename in files:
            # Check if filename matches the pattern
            if re.search(pattern, filename):
                filepath = os.path.join(directory, filename)
                
                # Open and process JSON file
                with open(filepath, 'r') as file:
                    data = json.load(file)
                    for k, v in data.items():
                        if k == "FAILURE_REASON" and v is not None:
                            errors.append(v)

                            
                            
    #for i in glob.glob(os.listdir(os.path.expanduser(folder))):
        #match = re.search(pattern, i)
        #if match:
            #filepath = str(folder + i)
            #with open(glob.glob(os.path.expanduser(filepath)), 'r') as file:
                #data = json.load(file)
            #for k,v in data.items():
                    #if k == "FAILURE_REASON" and v != None:
                        #errors.append(v)

#count number of each error
counted_errors = Counter(errors)

# Plot
alph_data = dict(counted_errors.most_common())
labels = [s.replace("_"," ") for s in list(alph_data.keys())]
values = list(alph_data.values())
fig = plt.figure(figsize = (20, 6))

# creating the bar plot
plt.bar(labels, values, color ='teal', 
        width = 0.5, zorder=2)

plt.grid(axis = 'y', zorder = 1)
plt.xlabel("Error Type")
plt.ylabel("No. Occurrences")
plt.title("Number of Errors of Each Type")
plt.xticks(rotation=-30, ha='left')
plt.tight_layout()
plt.savefig("1st_Probe_Card_Wafer_Errors.png")
plt.close()
    
print('1st probe card')
# Print the counts
for error, count in alph_data.items():
    print(f"{error}: {count}")

