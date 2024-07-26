#plots all tests and the number of chips with them on red, green, yellow, and gray graphs
#using _wafer_data files
import re
import os
import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np
from collections import Counter

#init
redtests = {}
yellowtests = {}
greentests = {}
graytests = {}
extra = {} #for chips/tests with status 3--what does that mean??

#open file
folderpaths = ['~/WLT/WLT_v1.4.1/croc_wlt/data/wafer_NC0W14-03B6/20240627_115829/plots/_wafer_data_NC0W14-03B6_20240627_115829.json', '~/WLT/WLT_v1.4.1/croc_wlt/data/wafer_NC0W14-04B1/20240624_164933/plots/_wafer_data_NC0W14-04B1_20240624_164933.json', '~/WLT/WLT_v1.4.1/croc_wlt/data/wafer_NC0W14-06H2/20240625_164506/plots/_wafer_data_NC0W14-06H2_20240625_164506.json']
for filepath in folderpaths:
    with open(os.path.expanduser(filepath), 'r') as file:
        data = json.load(file)

    for k,v in data.items(): #loop through lines of json file to find statistics dictionary
        if k == "statistics": 
            for test, stats in v.items(): #loop through the statistics dictionary, which contains each test
                if isinstance(stats, dict):
                    for a, b in stats.items(): #loop through the test's dictionary to get counts
                        if a == "counts":
                            for stat, count in b.items():
                                if stat == "-1":
                                    graytests.update({test: count})
                                elif stat == "0":
                                    greentests.update({test: count})
                                elif stat == "1":
                                    yellowtests.update({test: count})
                                elif stat == "2":
                                    redtests.update({test: count})
                                elif stat == "3":
                                    extra.update({test: count})
                                else:
                                    print(f'Stat does not exist: {stat} for test {test}')

#Data for each plot
keys_to_remove = []
for k, v in list(graytests.items()):  # Use list(my_dict.items()) to create a copy of the items to iterate over
    if v == 0:
        keys_to_remove.append(k)
        del graytests[k]    
alph_gray = dict(Counter(graytests).most_common())
gray_x = [s.replace("_"," ") for s in list(alph_gray.keys())]
gray_y = list(alph_gray.values())

keys_to_remove = []
for k, v in list(greentests.items()):  # Use list(my_dict.items()) to create a copy of the items to iterate over
    if v == 0:
        keys_to_remove.append(k)
        del greentests[k]    
alph_green = dict(Counter(greentests).most_common())
green_x = [s.replace("_"," ") for s in list(alph_green.keys())]
green_y = list(alph_green.values())

keys_to_remove = []
for k, v in list(yellowtests.items()):  # Use list(my_dict.items()) to create a copy of the items to iterate over
    if v == 0:
        keys_to_remove.append(k)
        del yellowtests[k]    
alph_yellow = dict(Counter(yellowtests).most_common())
yellow_x = [s.replace("_"," ") for s in list(alph_yellow.keys())]
yellow_y = list(alph_yellow.values())

keys_to_remove = []
for k, v in list(redtests.items()):  # Use list(my_dict.items()) to create a copy of the items to iterate over
    if v == 0:
        keys_to_remove.append(k)
        del redtests[k]    
alph_red = dict(Counter(redtests).most_common())
red_x = [s.replace("_"," ") for s in list(alph_red.keys())]
red_y = list(alph_red.values())

# creating the bar plots
def error_plot(statcolor, x, y, size):
    fig = plt.figure(figsize = size)
    plt.bar(x, y, color =statcolor, 
            width = 0.5, zorder=2)
    plt.grid(axis = 'y', zorder = 1)
    plt.xlabel("Test")
    plt.ylabel("No. Occurrences")
    plt.title(statcolor)
    plt.xticks(rotation=-30, ha='left', fontsize = 5)
    plt.tight_layout()
    plt.savefig(f'2nd_Probe_Card_{statcolor}_Errors.png')
    plt.close()
    for i in range(len(x)):
        print(f'{x[i]}: {y[i]}')

#error_plot(statcolor = "Gray", x=gray_x, y=gray_y, size=(40,12))
#error_plot(statcolor = "Green", x=green_x, y=green_y, size=(40,12))
#error_plot(statcolor = "Yellow", x=yellow_x, y=yellow_y, size=(20,6))
error_plot(statcolor = "Red", x=red_x, y=red_y, size=(20,6))
