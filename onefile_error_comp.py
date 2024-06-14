#Analyze errors of one file 
import re
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import numpy as np

#open file
with open('/nfshome/natpenn/Desktop/CROCv2-iter2/wafer_N61F26-15F3_20240413_022359.log', 'r') as file:
    log_content = file.readlines()

#Set up patterns
waferpattern = r'Wafer: (\w\w\w\w)'
waferid = ""
testabortpattern = r'Testing has been aborted for chip (.*)'
failedtestchips = []
pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| ChipTester \(\S\S\S\S\-(\w\w\)) \| ERROR    \| (.*)'
nochippattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| .* \((\S\S\S\S).*\| ERROR    \| (.*)'

#Find errors, names of aborted chips, and wafer ID
chip = ()
errors1 = ()
errors = []
nochiperror = ()
nochiperrors = []
for line in log_content:
    match = re.search(pattern, line)
    nochipmatch = re.search(nochippattern, line)
    if match:
        chip = str(match.group(2)) 
        chip = chip.replace(")","")
        errors1 = match.group(3) 
        errors.append(chip+errors1)
        testabortmatch = re.search(testabortpattern, line)
        if testabortmatch:
            failedtestchips.append(testabortmatch.group(1))
    elif nochipmatch:
        if nochipmatch.group(3) != "Waferprobing has been aborted!":
            errors.append("AA" + nochipmatch.group(3))
    wafermatch = re.search(waferpattern, line)
    if wafermatch:
        waferid = str(wafermatch.group(1))
    
print("Wafer ID: " + str(waferid))
print("Start date: " + str(str([log_content[0]])[:12][2:]))

#Remove duplicate errors (for each chip)
errors = list(set(errors))
errors = [i[2:] for i in errors]

#Process aborted chip counter
failedtestchips = [i[12:] for i in failedtestchips]
failedtestchips = [i[:2] for i in failedtestchips]

#error counter
scan_chain = 0
analog_scan = 0
digital_scan = 0
vdd = 0
register_error = 0
daq_func_prog_term = 0
dead_pixels = 0
testing_aborted = 0
test_end = 0
prog_err = 0
daq_digital = 0
daq_digital_2 = 0 #error message with the previous
dac_calibration = 0
dac_calibration_2 = 0 #error message with the previous
other_errors = []
pattern2 = r'Register .* failed the test'
pattern3 = r'Number of errors: .*'
xxx = 0

#count each error type
for x in errors:
    match2 = re.search(pattern2, x)
    match3 = re.search(pattern3, x)
    match4 = re.search(testabortpattern, x)
    if x==("Scan chain test failed!"):
        scan_chain = scan_chain + 1
    elif x==("Analog scan failed!"):
        analog_scan = analog_scan + 1
    elif x==("Digital scan failed!"):
        digital_scan = digital_scan + 1
    elif x==("DAQ function write_vdd_trim_bits terminated unexpectedly!"):
        vdd = vdd + 1
    elif x==("Register W&R errors detected!"):
        register_error = register_error + 1
    elif x==("DAQ function program terminated unexpectedly!"):
        daq_func_prog_term = daq_func_prog_term + 1
    elif x==("Waferprobing has been aborted!"):
        test_end = test_end + 1
    elif x==("Could not program the chip!"):
        prog_err = prog_err + 1
    elif x==("DAQ function digital_scan terminated unexpectedly!"):
        daq_digital = daq_digital + 1
    elif x==("Digital scan failed due to DAQ error!"):
        daq_digital_2 = daq_digital_2 + 1
    elif x==("DAQ function dac_calibration terminated unexpectedly!"):
        dac_calibration = dac_calibration + 1
    elif x==("DACs calibration failed! Continuing the testing..."):
        dac_calibration_2 = dac_calibration_2 + 1
    elif match2:
        dead_pixels = dead_pixels + 1
    elif match3:
        xxx = xxx + 1
    elif match4:
        testing_aborted = testing_aborted + 1
    else:
        other_errors.append(x)
    
#printing
print("------")
print("There were " + str(len(errors)+len(nochiperrors)) + " total error messages in 1 wafer.")
print("Number of scan chain errors: " + str(scan_chain))
print("Number of analog scan failures: " + str(analog_scan))
print("Number of digital scan failures: " + str(digital_scan))
print("Number of VDD errors: " + str(vdd))
print("Number of chips with dead pixels: " + str(register_error))
print("Number of DAQ function program terminations:" + str(daq_func_prog_term))
print("Number of programming errors: " + str(prog_err))
print("Number of DAQ digital scan errors: " + str(daq_digital))
print("Number of DAC calibration errors: " + str(dac_calibration))
print("------")
if testing_aborted > 0:
    print(str(testing_aborted) + " chip(s) did not complete testing (" + ', '.join(failedtestchips) + ").")
elif testing_aborted == 0:
    print("All chips completed testing")
print("Total number of dead pixels: " + str(dead_pixels) + " (of 145152 in 1 wafer)")
print("Other errors (" + str(len(other_errors)) + "): ") 
for error in other_errors:
    print("   - " + str(error))

# Plot
data = {'Scan Chain Errors':scan_chain,'VDD':vdd,'Dead Pixels':register_error,'Digital Scan':digital_scan,'DAQ Func Prog Term':daq_func_prog_term,'DAQ Digital Scan':daq_digital,'Analog Scan':analog_scan,'DAC Calibration':dac_calibration,'other':len(other_errors)}

alph_data = dict(sorted(data.items()))
clean_data = {k:v for k,v in alph_data.items() if v > 0}
labels = list(clean_data.keys())
values = list(clean_data.values())

fig = plt.figure(figsize = (10, 6))

# creating the bar plot
plt.bar(labels, values, color ='teal', 
        width = 0.5, zorder=2)

plt.grid(axis = 'y', zorder = 1)
plt.xlabel("Error Type")
plt.ylabel("No. Occurrences")
plt.title("Number of Errors of Each Type")
plt.xticks(rotation=-30, ha='left')

#save as file
now = datetime.now()
current_dt = now.strftime("%m-%d-%Y.%H:%M:%S")

#plt.savefig(str(current_dt) + '.CROCerrortest.pdf')
plt.savefig(str(current_dt) + '.Wafer' + str(waferid) + 'errors.png')




        


