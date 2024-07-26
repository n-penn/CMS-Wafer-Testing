#Script to track analog and digital contact resistance over time
#Credit to Weston Schwartz for the original script
#Run in terminal with argument 1 as analog or digital and argument 2 as the file path to the log file 
import re
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

#Check system arguments
if len(sys.argv) == 3:
    test_type = sys.argv[1]
    file_path = sys.argv[2]
else:
    print(f"Error: please provide a valid number of command-line arguments")
    sys.exit(1)

if not os.path.isfile(file_path):
    print(f"Error: '{file_path}' is not a valid file path.")
    sys.exit(1)

#Open file
try:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
        log_content = file.readlines()
except FileNotFoundError:
    print(f"Error: File '{file_path}' not found.")
except IOError as e:
    print(f"Error: {e}")
    
#Get wafer id
waferbatch_pattern = r'.*Batch: (.*)'
waferid_pattern = r'.*Wafer: (.*)'
wafer_batch = ''
wafer_id = ''
for line in log_content:
    waferbatch_match = re.search(waferbatch_pattern, line)
    waferid_match = re.search(waferid_pattern, line)
    if waferbatch_match:
        wafer_batch = waferbatch_match.group(1)
    if waferid_match:
        wafer_id = waferid_match.group(1)

#Search for contact resistance values and times
if test_type == 'analog':
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Contact resistance \(analog\): (\d+\.\d+) ohm'
elif test_type == 'digital':
    pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Contact resistance \(digital\): (\d+\.\d+) ohm'
else:
    print("Error: please provide a valid test type (analog or digital)")
    sys.exit(1)
time_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Performing periodic cleaning of the needles'
timestamps = []
resistances = []
for line in log_content:
    match = re.search(pattern, line)
    if match:
        timestamp = match.group(1)
        resistance = float(match.group(2))  # Convert resistance to float
        timestamps.append(timestamp)
        resistances.append(resistance)

#Search for cleaning times        
times = []
for i in log_content:
    good = re.search(time_pattern, i)
    if good:
        time = good.group(1)
        times.append(time)

#Set dates
dates = [datetime.strptime(f'{ts}', '%Y-%m-%d %H:%M:%S,%f') for ts in timestamps]

#Plot
plt.figure(figsize=(12, 6))
plt.plot(dates, resistances, marker='o', linestyle='-', color='teal')

#Add vertical lines for each time in the times list
for time in times:
    time_dt = datetime.strptime(f'{time}', '%Y-%m-%d %H:%M:%S,%f')
    hour_minute = time_dt.strftime('%H:%M')
    plt.axvline(x=time_dt, color='crimson', linestyle='--')
    plt.text(time_dt, plt.gca().get_ylim()[1], hour_minute, ha='center', va='bottom', color='crimson', fontsize=8)

#Format the x-axis
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=1))
plt.gcf().autofmt_xdate()

#Set labels and title
plt.xlabel('Time')
plt.ylabel('Resistance (ohm)')
plt.title(f'Analog Resistance vs. Time (Wafer {wafer_batch}-{wafer_id}', y=1.05)

#Get 16 evenly spaced indices from the dates list
indices = np.linspace(0, len(dates) - 1, num=16, dtype=int)

#Use the indices to get the corresponding dates and set them as tick locations and labels
plt.xticks([dates[i] for i in indices], [dates[i].strftime('%H:%M') for i in indices])

#Save plot
plt.show()
file_path = "~/Desktop/CMS-Wafer-Testing/Contact-Resistance/"
file_name = os.path.expanduser(os.path.join(file_path, f'Contact_resistance_{test_type}_{wafer_batch}-{wafer_id}.jpg'))
plt.savefig(file_name)
print(f'File saved to ~/Desktop/CMS-Wafer-Testing/Contact-Resistance/{file_name}')
