#Analyze errors of all files in a folder
#Entire document title here, leave blank for no title:
TITLE = "1st probe card"

import re
import os
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib as mpl
from datetime import datetime
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, flowables
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
import time

#Find errors, names of aborted chips, and wafer ID
chip = ()
errors1 = ()
errors = []
nochiperror = ()
nochiperrors = []
wafercount = 0

#Set up patterns
waferpattern = r'Wafer: (\w\w\w\w)'
waferid = ""
testabortpattern = r'Testing has been aborted for chip (.*)'
failedtestchips = []
pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| ChipTester \(\S\S\S\S\-(\w\w\)) \| ERROR    \| (.*)'
nochippattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| .* \((\S\S\S\S).*\| ERROR    \| (.*)'
allwaferids = []        

#open file
if len(sys.argv) != 2:
    print("Usage: python script_name.py <file_path>")
    sys.exit(1)
file_path = sys.argv[1]
path = os.path.expanduser(file_path)
for file_name in os.listdir(path):
    if file_name.endswith(".log"):
        file_path = os.path.join(path, file_name)
        wafercount = wafercount + 1
        with open(file_path, 'r') as file:
            log_content = file.readlines()
        
        #Find errors, names of aborted chips, and wafer ID
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
                allwaferids.append(waferid)
        print("Wafer ID: " + str(waferid))
        print("Start date: " + str(str([log_content[0]])[:12][2:]))
        
#Remove duplicate errors (for each chip)
errors = list(set(errors))
errors = [i[2:] for i in errors]

#Process aborted chip counter
failedtestchips = [i[12:] for i in failedtestchips]
failedtestchips = [i[:2] for i in failedtestchips]

#error counter
real_errors = 0
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
pixel_register = 0
daq_digital = 0
daq_digital_2 = 0 #error message with the previous
dac_calibration = 0
dac_calibration_2 = 0 #error message with the previous
temps = 0
ldo = 0
iref = 0
threshold = 0
overvoltage = 0
data_merging = 0
other_errors = []
pattern2 = r'Register .* failed the test'
pattern3 = r'Number of errors: .*'
xxx = 0
repeats = 0

#count each error type
for x in errors:
    match2 = re.search(pattern2, x)
    match3 = re.search(pattern3, x)
    match4 = re.search(testabortpattern, x)
    if 'Scan chain test failed!' in x:
        scan_chain = scan_chain + 1
        real_errors = real_errors + 1
    elif x==("Analog scan failed!"):
        analog_scan = analog_scan + 1
        real_errors = real_errors + 1
    elif x==("Digital scan failed!"):
        digital_scan = digital_scan + 1
        real_errors = real_errors + 1
    elif x==("DAQ function write_vdd_trim_bits terminated unexpectedly!") or 'VDD' in x:
        vdd = vdd + 1
        real_errors = real_errors + 1
    elif x==("Register W&R errors detected!"):
        register_error = register_error + 1
        real_errors = real_errors + 1
    elif x==("DAQ function program terminated unexpectedly!"):
        daq_func_prog_term = daq_func_prog_term + 1
        real_errors = real_errors + 1
    elif x==("Waferprobing has been aborted!"):
        test_end = test_end + 1
        real_errors = real_errors + 1
    elif x==("Could not program the chip!"):
        prog_err = prog_err + 1
        real_errors = real_errors + 1
    elif x==("Pixel registers test failed!"):
        pixel_register = pixel_register + 1
        real_errors = real_errors + 1
    elif x==("DAQ function digital_scan terminated unexpectedly!"):
        daq_digital = daq_digital + 1
        real_errors = real_errors + 1
    elif x==("DAQ function dac_calibration terminated unexpectedly!") or x==("DACs calibration failed!"):
        dac_calibration = dac_calibration + 1
        real_errors = real_errors + 1
    elif x==("Could not measure chip temperatures!"):
        temps = temps + 1
        real_errors = real_errors + 1
    elif x==("Measured values in LDO mode not within tolerance!"):
        ldo = ldo + 1
        real_errors = real_errors + 1
    elif x==("IREF trimming failed online selection!"):
        iref = iref + 1
        real_errors = real_errors + 1
    elif x==("Threshold scan failed!"):
        threshold = threshold + 1
        real_errors = real_errors + 1
    elif x==("A chip trip condition has been detected! Digital power: ['overvoltage_trip']"):
        overvoltage = overvoltage + 1
        real_errors = real_errors + 1
    elif x==("Data merging test failed!"):
        data_merging = data_merging + 1
        real_errors = real_errors + 1
    elif match2:
        dead_pixels = dead_pixels + 1
    elif match3:
        xxx = xxx + 1
    elif match4:
        testing_aborted = testing_aborted + 1
    elif x==("Aborting testing") or x==("Digital scan failed online cuts!") or x==("Aborting testing!") or x==("Digital scan failed before completion!") or x==("Analog scan failed online cuts!") or x==("Coarse threshold scan failed!") or x==("Threshold scan failed due to DAQ error!") or x==("DAQ function read_temperature terminated unexpectedly!") or x==("Digital scan failed") or x==("Digital scan failed due to DAQ error!") or x==("DACs calibration failed! Continuing the testing...") or x==("Testing of pixel registers failed!") or x==("More than 150 register errors!") or x==("Failing pixel registers above online cut!") or x==("DAQ function threshold_scan terminated unexpectedly!"):
        repeats = repeats + 1
        real_errors = real_errors + 1
    else:
        other_errors.append(x)
        real_errors = real_errors + 1

#printing
print("Wafer ID: " + str(allwaferids))
print("Start date: " + str(str([log_content[0]])[:12][2:]))
print("------")
print(f'There were {str(len(errors)+len(nochiperrors))} total error messages and {real_errors} actual errors in {len(allwaferids)} wafer(s). {repeats} were repeats and will not be shown below.') 
print("Number of scan chain errors: " + str(scan_chain))
print("Number of analog scan failures: " + str(analog_scan))
print("Number of digital scan failures: " + str(digital_scan))
print("Number of VDD errors: " + str(vdd))
print("Number of chips with dead pixels: " + str(register_error))
print("Number of DAQ function program terminations: " + str(daq_func_prog_term))
print("Number of programming errors: " + str(prog_err))
print("Number of DAQ digital scan errors: " + str(daq_digital))
print("Number of DAC calibration errors: " + str(dac_calibration))
print("Number of temperature measurement errors: " + str(temps))
print("Number of LDO measurement errors: " + str(ldo))
print("Number of IREF trimming failures: " + str(iref))
print("Number of threshold scan failures: " + str(threshold))
print("Number of overvoltage trip errors: " + str(overvoltage))
print("Number of data merging errors: " + str(data_merging))
print("------")

#use if there are errors with test ending to match with number of total tests
if test_end == 1:
    print("Test ended")
elif test_end == 0:
    print("Test end error")
else:
    print(str(test_end) + " Tests ended")
if testing_aborted > 0:
    #testing_message = f"{testing_aborted} chip(s) did not complete testing (chip ID(s): {', '.join(failedtestchips)})."
    testing_message = f"{testing_aborted} chip(s) did not complete testing."
elif testing_aborted == 0:
    testing_message = "All chips completed testing"

# Plot
mpl.rcParams.update({'font.size': 18})
data = {'Scan Chain':scan_chain,'VDD':vdd,'Dead Pixels':register_error,'Digital Scan':digital_scan,'DAQ Func Prog Term':daq_func_prog_term,'Temperature Measurement':temps,'Data Merging':data_merging,'Overvoltage Trip':overvoltage,'Threshold Scan':threshold,'IREF trimming':iref,'LDO mode':ldo,'DAQ Digital Scan':daq_digital,'Analog Scan':analog_scan,'DAC Calibration':dac_calibration,'other':len(other_errors)}

alph_data = dict(sorted(data.items()))
clean_data = {k:v for k,v in alph_data.items() if v > 0}
labels = list(clean_data.keys())
values = list(clean_data.values())
fig = plt.figure(figsize = (12, 12))

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
plt.tight_layout()
plt.savefig("plot.png")
plt.close()

#Saving to PDF
def save_to_pdf(output_filename, waferid, log_content, errors, nochiperrors, scan_chain, analog_scan, digital_scan, vdd, register_error, daq_func_prog_term, prog_err, daq_digital, dac_calibration, temps, ldo, iref, threshold, overvoltage, data_merging, testing_message, dead_pixels, other_errors, plot_filename):
    # Create a new PDF file
    can = canvas.Canvas(output_filename, pagesize=letter)
    # Define text content
    style_sheet = getSampleStyleSheet()
    style_sheet['Normal'].fontName = 'Times-Roman'
    normal_style = style_sheet['Normal']
    text_content = [
        f"Wafer ID: {', '.join(allwaferids)}",
        f"Start date: {str(log_content[0])[:10]}",
        "------",
        f'There were {str(len(errors)+len(nochiperrors))} total error messages and {real_errors} actual errors in {len(allwaferids)} wafer(s). {repeats} were repeats and will not be shown below.',
        f"Number of scan chain errors: {str(scan_chain)}",
        f"Number of analog scan failures: {str(analog_scan)}",
        f"Number of digital scan failures: {str(digital_scan)}",
        f"Number of VDD errors: {str(vdd)}",
        f"Number of chips with dead pixels: {str(register_error)}",
        f"Number of DAQ function program terminations: {str(daq_func_prog_term)}",
        f"Number of programming errors: {str(prog_err)}",
        f"Number of DAQ digital scan errors: {str(daq_digital)}",
        f"Number of DAC calibration errors: {str(dac_calibration)}",
        f"Number of temperature measurement errors: {temps}",
        f"Number of LDO measurement errors: {ldo}",
        f"Number of IREF trimming failures: {iref}",
        f"Number of threshold scan failures: {threshold}",
        f"Number of overvoltage trip errors: {overvoltage}",
        f"Number of data merging errors: {data_merging}",
        f"{testing_message}",
        f"Total number of dead pixels: {str(dead_pixels)} (of {145152*len(allwaferids)} in {len(allwaferids)} wafer(s))",
        f"Other errors ({str(len(other_errors))}):" 
    ]

    for error in other_errors:
        text_content.append(f"   - {str(error)}")

    # Set initial y position for text
    y = 720

    # Write content to the PDF
    can.setFont('Times-Roman', 20)
    if len(TITLE) > 0:
        can.drawString(72, y, TITLE) 
        y-= 20
    for line in text_content:
        leading_spaces = len(line) - len(line.lstrip()) #to help other_errors format as bullet points
        if leading_spaces > 0:
            leading_spaces_width = can.stringWidth(" " * leading_spaces)
            if y<40:
                can.showPage()
                y = 720
            paragraph = Paragraph(line, style_sheet['Normal'])
            width, height = paragraph.wrap(468, 720)
            paragraph.drawOn(can, 72 + leading_spaces_width, y - height)
            y -= (height + 4)
        else:
            if y<40:
                can.showPage()
                y = 720
            paragraph = Paragraph(line, style_sheet['Normal'])
            width, height = paragraph.wrap(468, 720)
            paragraph.drawOn(can, 72, y - height)
            y -= (height + 4)

    #Add second page
    can.showPage()
    can.drawImage(plot_filename, 72, 162, width=468, height=468)
    can.save()
    print(f'PDF saved to {output_filename}')

now = datetime.now()
current_dt = now.strftime("%m-%d-%Y.%H:%M:%S")
if __name__ == '__main__':
    output_filename = f"{current_dt}.Wafer{','.join(allwaferids)}errors.pdf"
    plot_filename = "plot.png"
    save_to_pdf(output_filename, waferid, log_content, errors, nochiperrors, scan_chain, analog_scan, digital_scan, vdd, register_error, daq_func_prog_term, prog_err, daq_digital, dac_calibration, temps, ldo, iref, threshold, overvoltage, data_merging, testing_message, dead_pixels, other_errors, plot_filename)
