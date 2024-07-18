#run this script after starting wafertester
#note: must have config file in the same folder as this (?maybe)
import os
import re
import glob
from datetime import datetime, date
import configparser
import email
from email.header import decode_header 
from email.message import EmailMessage
import getpass
import imaplib
import smtplib
import ssl
import time

#Starting message
print('Starting Wafer-Tester-Status script. Please do not close this script until wafer testing has completed. For more information, please visit https://github.com/n-penn/CMS-Wafer-Testing/')

#config
N1 = 2 #consecutive chips that report any error
N2 = 2 #consecutive chips that report the same error
testing_order = ['81', '71', '61', '42', '52', '62', '72', '82', '92', 'A2', 'B3', 'A3', '93', '83', '73', '63', '53', '43', '33', '24', '34', '44', '54', '64', '74', '84', '94', 'A4', 'B4', 'C5', 'B5', 'A5', '95', '85', '75', '65', '55', '45', '35', '25', '26', '36', '46', '56', '66', '76', '86', '96', 'A6', 'B6', 'C6', 'C7', 'B7', 'A7', '97', '87', '77', '67', '57', '47', '37', '27', '17', '18', '28', '38', '48', '58', '68', '78', '88', '98', 'A8', 'B8', 'C8', 'D8', 'C9', 'B9', 'A9', '99', '89', '79', '69', '59', '49', '39', '29', '19', '2A', '3A', '4A', '5A', '6A', '7A', '8A', '9A', 'AA', 'BA', 'CA', 'CB', 'BB', 'AB', '9B', '8B', '7B', '6B', '5B', '4B', '3B', '2B', '3C', '4C', '5C', '6C', '7C', '8C', '9C', 'AC', 'BC', 'BD', 'AD', '9D', '8D', '7D', '6D', '5D', '4D', '3D', '4E', '5E', '6E', '7E', '8E', '9E', '7F', '6F']

#initialize
waferfinished = 'False'
last_line = 0
cons_chips_with_errors = []
sent_error_chips = []
chip_error_dict = {}
error_line_dict = {}

#define functions
def find_consecutive_sequences(a, b, N1): #function to find consecutive sequences (chips)
    consecutive_sequences = []
    i = 0
    while i < len(b):
        current_sequence = [b[i]]
        j = i + 1
        while j < len(b):
            if b[j] == a[a.index(current_sequence[-1]) + 1]:
                current_sequence.append(b[j])
            else:
                break
            j += 1
        if len(current_sequence) >= N1:
            consecutive_sequences.extend(current_sequence) #use append for groups of lists
            i = j  # Move to the next element after the found sequence
        else:
            i += 1
    return consecutive_sequences

def read_log_file(): #open the most recent log file
    #initialize
    root_dir = glob.glob(os.path.expanduser('~/WLT/WLT_v1.2.1/croc_wlt/data'))[0]
    if os.path.exists(root_dir):
        print(f"Directory '{root_dir}' exists.")
    else:
        print(f"Directory '{root_dir}' does not exist.")
    most_recent_dir = None
    most_recent_time = datetime.min

    folder_pattern = r'wafer\_\S\S\S\S\S\S\-\S\S\S\S'
    #find most recent wafer folder
    for folder in os.listdir(root_dir):
        if os.path.isdir(os.path.join(root_dir, folder)):
            folder_match = re.search(folder_pattern, folder)
            if folder_match:
                full_path = os.path.join(root_dir, folder)
                modified_time = datetime.fromtimestamp(os.path.getmtime(full_path))
                if modified_time > most_recent_time:
                    most_recent_time = modified_time
                    most_recent_dir = full_path
    print(f'Most recent directory: {most_recent_dir}')
    #find most recent subdirectory
    most_recent_subdir = None
    most_recent_time = datetime.min
    if most_recent_dir:
        for folder in os.listdir(most_recent_dir):
            if os.path.isdir(os.path.join(most_recent_dir, folder)):
                full_path = os.path.join(most_recent_dir, folder)
                modified_time = datetime.fromtimestamp(os.path.getmtime(full_path))
                if modified_time > most_recent_time:
                    most_recent_time = modified_time
                    most_recent_subdir = full_path
    print(f'Most recent subdirectory: {most_recent_subdir}')
    
    #find most recent log file
    most_recent_file = None
    most_recent_time = None

    # Iterate through all files in the directory
    for filename in os.listdir(most_recent_subdir):
        if filename.endswith(".log"):  # Check if file ends with .log
            file_path = os.path.join(most_recent_subdir, filename)
            modification_time = os.path.getmtime(file_path)

            # Update most_recent_file and most_recent_time if current file is more recent
            if most_recent_time is None or modification_time > most_recent_time:
                most_recent_time = modification_time
                most_recent_file = file_path

    # Check if a most recent log file was found
    if most_recent_file:
        #print(f"The most recent log file is: {most_recent_file}")
        #print(f"Last modified time: {datetime.fromtimestamp(most_recent_time)}")
        pass
    else:
        print("No log files found in the directory.")
    with open(most_recent_file, 'r') as file:
        log_content = file.readlines()
    return log_content

def get_status(): #calculates all variables that refer to the status of the wafer
    log_content = read_log_file()
    waferid = ''
    waferfinished = 'False'
    waferstatus = 'Still testing'
    testing_completed = 'Still testing'
    chips_to_test = 0
    chips_tested = []
    chips_aborted = 0
    resistances = []
    waferid_pattern = r'.* Wafer: (.*)'
    testing_completed_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) .* Completed testing of wafer (.*)' #see if the wafer is finished testing, and if it is, what time it finished
    wafer_aborted_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*Waferprobing has been aborted!'
    chips_to_test_pattern = r'.* Chips to test: (.*)' #find number of chips to test
    chip_complete_pattern = r'.*\(\S\S\S\S\-(.*)\).*Completed testing of chip.*' #number of chips tested
    chips_aborted_pattern = r'.*\(\S\S\S\S\-(.*)\).*Testing has been aborted for chip.*'
    analog_contact_pattern = r'.*Contact resistance \(analog\): (\d+\.\d+) ohm'
    for line in log_content:
        waferid_match = re.search(waferid_pattern, line)
        tcmatch = re.search(testing_completed_pattern, line)
        wamatch = re.search(wafer_aborted_pattern, line)
        chips_to_test_match = re.search(chips_to_test_pattern, line)
        chip_complete_match = re.search(chip_complete_pattern, line)
        chips_aborted_match = re.search(chips_aborted_pattern, line)
        analog_contact_match = re.search(analog_contact_pattern, line)
        if waferid_match: 
            waferid = waferid_match.group(1)
        if wamatch:
            waferfinished = 'True'
            testing_completed = wamatch.group(1)
            waferstatus = 'Testing aborted'
        if tcmatch:
            waferfinished = 'True'
            testing_completed = tcmatch.group(1)
            if waferstatus != 'Testing aborted':  #This is separate so tcmatch doesn't overwrite waferstatus after wamatch has updated it
                waferstatus = 'Testing completed successfully'
        if chips_to_test_match:
            chips_to_test = chips_to_test_match.group(1)
        if chip_complete_match:
            chips_tested.append(chip_complete_match.group(1))
        if chips_aborted_match:
            chips_aborted += 1
        if analog_contact_match:
            resistances.append(analog_contact_match.group(1))
    chips_tested = list(set(chips_tested))
    
    #find current chip, if any
    currentpattern = r'.*ChipTester.*\(\S\S\S\S\-(.*)\).*'
    current_chip = 'None'
    for line in reversed(log_content):
        currentmatch = re.search(currentpattern, line)
        if currentmatch:
            current_chip = currentmatch.group(1)
            break
    
    #find last completed chip, if any
    lastpattern = r'.*\(\S\S\S\S\-(.*)\).*Completed testing of chip.*'
    last_tested = 'None'
    for line in reversed(log_content):
        lastmatch = re.search(lastpattern, line)
        if lastmatch:
            last_tested = lastmatch.group(1)
            break
    
    #find elapsed time
    timepattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*'
    firsttimematch = re.search(timepattern, log_content[0])
    finaltimematch = re.search(timepattern, log_content[len(log_content)-1])
    first_time = firsttimematch.group(1)
    first_dt = datetime.strptime(first_time, "%Y-%m-%d %H:%M:%S,%f")
    final_time = finaltimematch.group(1)
    final_dt = datetime.strptime(final_time, "%Y-%m-%d %H:%M:%S,%f")
    time_diff = final_dt - first_dt
    time_format = "%H:%M:%S.%f"
    dt = datetime.strptime(str(time_diff), time_format)
    hours = dt.hour
    minutes = dt.minute
    seconds = dt.second
    microseconds = dt.microsecond
    time_elapsed = str(hours) + 'h ' + str(minutes) + 'm ' + str(seconds) + 's'
    
    #est time remaining, based off number of chips completed and chips to test number FIXME THIS IS WRONG
    complete = len(chips_tested) + chips_aborted
    remaining = int(chips_to_test) - int(complete)
    time_remaining = 1
    if remaining > 0:
        time_remaining = remaining * 8 #est. time remaining in minutes
    elif remaining == 0:
        time_remaining = 0
    elif remaining < 0:
        time_remaining = 'undefined'
    
    #average contact resistance
    resistances = [float(r) for r in resistances]
    if len(resistances) == 0:
        analog_contact_avg = 0
    else:
        contact_sum = sum(resistances)
        analog_contact_avg = int(contact_sum) / len(resistances)
    
    #errors
    errorlines = []
    for line in log_content:
        regular_match = re.search(timepattern, line) #find lines that do not fit the regular 
        if not regular_match: 
            errorlines.append(line)
    errorlines = list(filter(lambda line: line.strip() != '', errorlines)) #remove blank lines
    
    #find chips with errors, then add to the chip error and error line dictionaries
    chip_error_pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) \| ChipTester \(\S\S\S\S\-(\w\w)\) \| ERROR    \| (.*)'
    global last_line
    for i in range(last_line, len(log_content)):
        line = log_content[i]
        chip_error_match = re.search(chip_error_pattern, line)
        if chip_error_match:
            chip_id = chip_error_match.group(2)
            error = chip_error_match.group(3)
            if chip_id in chip_error_dict:
                chip_error_dict[chip_id].append(error)
            else:
                chip_error_dict[chip_id] = [error]
            if chip_id in error_line_dict:
                error_line_dict[chip_id].append(str(i+1))
            else:
                error_line_dict[chip_id] = [str(i+1)]
        if last_line < i:
            last_line = i
    #use find_consecutive_sequences to find consecutive error chips and add them to the list
    to_add = find_consecutive_sequences(testing_order, list(chip_error_dict.keys()), N1)
    for item in to_add:
        cons_chips_with_errors.append(item)

    #return variables
    return log_content, waferid, waferfinished, waferstatus, testing_completed, chips_tested, chips_aborted, current_chip, last_tested, final_dt, time_elapsed, time_remaining, analog_contact_avg, errorlines, cons_chips_with_errors, error_line_dict

def send_status(sender, subject, body): #add to the body of the email to be sent
    to_body = ''
    status = get_status()
    if isinstance(status, tuple) and len(status) == 16:
        log_content, waferid, waferfinished, waferstatus, testing_completed, chips_tested, chips_aborted, current_chip, last_tested, final_dt, time_elapsed, time_remaining, analog_contact_avg, errorlines, cons_chips_with_errors, error_line_dict = status
    else:
        print("Error occurred in get_status()")
    #add to body
    if waferfinished == 'True':
        to_body += f'Wafer finished at {testing_completed}.\n'
    if waferfinished == 'False':
        to_body += f'Wafer has not completed.\n'
    if "current" or "all" in body: #print last started chip
        if current_chip == 'None':
            to_body += f'No chips have begun testing.\n'
        else:
            to_body += f'Current chip: {current_chip}\n'
    if "last" or "all" in body: #print last completed chip
        if last_tested == 'None':
            to_body += f'No chips have completed testing.\n'
        else:
            to_body += f'Last completed chip: {last_tested}\n'
    if "chips" or "all" in body: #print number of chips that have completed testing
        if len(chips_tested) == 0 and "last" not in body: #don't want to repeat this line
            to_body += f'No chips have completed testing.\n'
        if len(chips_tested) != 0:
            to_body += f'{len(chips_tested)} chips have completed testing.\n'
    if "time" or "all" in body:
        to_body += f'Time elapsed: {time_elapsed}\n'
    if "contact" or "all" in body:
        to_body += f'Average contact resistance: {round(analog_contact_avg, 3)}'
        
    #return variables
    return to_body, waferid, waferstatus

def read_mailing_list(file_name): #opens mailing list file as a list
    try:
        with open(file_name, 'r') as file:
            emails = file.read().splitlines()
            return emails
    except FileNotFoundError:
        return []
    
def write_mailing_list(file_name, em_address): #writes to the mailing list file
    with open(file_name, 'w') as file:
        file.write(em_address + '\n')

def add_email(sender): #add the sender's email to mailing list
    file_name = os.path.expanduser('~/Desktop/CMS-Wafer-Testing/mailing_list.txt')
    emails = read_mailing_list(file_name)
    if sender not in emails:
        write_mailing_list(file_name, sender)
    print(f'Email added: {sender}')

def remove_email(sender): #remove sender's email from mailing list
    file_name = os.path.expanduser('~/Desktop/CMS-Wafer-Testing/mailing_list.txt')
    emails = read_mailing_list(file_name)
    with open(file_name, 'w') as file:
        for entry in emails:
            if entry != sender:
                file.write(email)
    print(f"Email '{sender}' removed successfully from '{file_name}'.")

def send_email(sender, subject, body): #actually sends the email to the person who requested it
    #Setting variables
    global to_email
    to_email = sender
    global to_body
    to_body, waferid, waferstatus = send_status(sender, subject, body)
    now = datetime.now()
    now = now.strftime("%m-%d-%Y %H:%M:%S")
    to_subject = f'Wafer {waferid} Status: {waferstatus} ({now})'
    
    #Actually sending email:
    em = EmailMessage()
    em['From'] = FROM_EMAIL
    em['To'] = to_email
    em['Subject'] = to_subject
    em.set_content(to_body)
    context = ssl.create_default_context() #Set SSL security
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
        smtp.login(FROM_EMAIL, FROM_PWD)
        smtp.sendmail(FROM_EMAIL, to_email, em.as_string())
    
    #Returning variables (for testing)
    return to_email, to_subject, to_body

#Set up main loop here
def check():
    #read config file for email and password
    config = configparser.ConfigParser()
    config.read('config.ini')
    global FROM_EMAIL
    FROM_EMAIL = config.get('Gmail', 'email')
    global FROM_PWD
    FROM_PWD = config.get('Gmail', 'passcode')
    global SMTP_SERVER
    SMTP_SERVER = "imap.gmail.com" 
    global SMTP_PORT
    SMTP_PORT = 993 

    #log in to email
    mail = imaplib.IMAP4_SSL(SMTP_SERVER)
    mail.login(FROM_EMAIL,FROM_PWD)

    # Select the mailbox (inbox)
    mail.select('inbox')

    # Search for all unread emails
    result, data = mail.search(None, 'UNSEEN')

    # `data` contains a space-separated string of UIDs
    if result == 'OK':
        unread_email_uids = data[0].split()
    else:
        unread_email_uids = []

    # Process each unread email
    for uid in unread_email_uids:
        # Fetch the email using UID
        result, data = mail.fetch(uid, '(RFC822)')
        if result == 'OK':
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)

            # Extract data from the email_message
            sender = email_message['From']
            subject = decode_header(email_message['Subject'])[0][0]
            if isinstance(subject, bytes):
                subject = subject.decode()

            # Extract body (assuming it's plain text)
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        body = part.get_payload(decode=True).decode()
                        break
            else:
                body = email_message.get_payload(decode=True).decode()

            # Perform different actions based on the email content
            print(f"Sender: {sender}")
            print(f"Subject: {subject}")
            print(f"Body:\n{body}")

            #Perform funcitons based on subject
            if ("Status" or "status") in subject:
                to_email = sender
                send_email(sender, subject, body)
            if ("Add" or "add") in subject:
                add_email(sender)
            if "remove" in subject or "Remove" in subject:
                remove_email(sender)
            # Mark the email as read
            mail.store(uid, '+FLAGS', '\Seen')

    log_content, waferid, waferfinished, waferstatus, testing_completed, chips_tested, chips_aborted, current_chip, last_tested, final_dt, time_elapsed, time_remaining, analog_contact_avg, errorlines, cons_chips_with_errors, error_line_dict = get_status()

    #ONLY let this run if it's inside the loop or if mailing_list.txt is blank

    #send email if there are N1 or more consecutive chips that have errors
    #make a list of any new error chips (within sequences) that haven't been sent yet so this doesn't keep sending emails while it runs
    chips_to_send = []
    for chip in cons_chips_with_errors:
        if chip not in sent_error_chips:
            chips_to_send.append(chip)
    #use this for actually sending emails
    if len(chips_to_send) >= N1:
        lines = []
        for chip in chips_to_send:
            if chip in error_line_dict:
                for line_no in error_line_dict[chip]:
                    lines.append(line_no)
            sent_error_chips.append(chip)
        to_body = f'Offending lines:\n\n'        
        for line in lines:
            to_body += f'{line} {log_content[int(line)-1]}\n'
        now = datetime.now()
        now = now.strftime("%m-%d-%Y %H:%M:%S")
        to_subject = f'Warning: 3 or more consecutive chips with errors for Wafer {waferid} at {now}!'
    if len(errorlines) > 0:
            to_body = to_body + f'Other possible errors: \n\n'
            for error in errorlines:
                to_body = to_body + f'{error}\n'
    file_name = os.path.expanduser('~/Desktop/CMS-Wafer-Testing/mailing_list.txt')
    mailing_list = read_mailing_list(file_name)
    #Actually sending email to each address in the file
    for item in mailing_list:
        to_email = item
        em = EmailMessage()
        em['From'] = FROM_EMAIL
        em['To'] = to_email
        em['Subject'] = to_subject
        em.set_content(to_body)
        context = ssl.create_default_context() #Set SSL security
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(FROM_EMAIL, FROM_PWD)
            smtp.sendmail(FROM_EMAIL, to_email, em.as_string())
        print(f'Sent email to {email}')
        
    #Send email if wafer is finished
    if waferfinished == 'True':
        now = datetime.now()
        now = now.strftime("%m-%d-%Y %H:%M:%S")
        to_subject = f'{waferstatus} for Wafer {waferid} at {now}!'
        to_body = f'The wafer has finished testing at {final_dt} and the elapsed time is {time_elapsed}.\n{len(chips_tested)} chips were completed.\n'
        if len(errorlines) > 0:
            to_body = to_body + f'Possible errors: \n'
            for error in errorlines:
                to_body = to_body + f'{error}\n'
        file_name = os.path.expanduser('~/Desktop/CMS-Wafer-Testing/mailing_list.txt')
        mailing_list = read_mailing_list(file_name)
        #Actually sending email to each address in the file
        for item in mailing_list:
            to_email = item
            em = EmailMessage()
            em['From'] = FROM_EMAIL
            em['To'] = to_email
            em['Subject'] = to_subject
            em.set_content(to_body)
            context = ssl.create_default_context() #Set SSL security
            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
                smtp.login(FROM_EMAIL, FROM_PWD)
                smtp.sendmail(FROM_EMAIL, to_email, em.as_string())
            print(f'Sent email to {email}')
            
    mail.close() #close mailbox
    mail.logout() #end imap session
    
    # Simulating a condition check
    return waferfinished 

# Main loop to run every five minutes until condition is met
while waferfinished == 'False':
    waferfinished = check()  
    if waferfinished == 'True':
        print('Testing complete, ending Wafer-Tester-Status script.')
        break
    time.sleep(30)  # Sleep for 30 seconds 
