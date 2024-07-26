# CMS-Wafer-Testing
Contents of this project:
  - Jupyter and python scripts to analyze and compare the frequency of errors in wafer testing
  - Python script to analyze the contact resistance over time of a wafer test
  - Python scripts to map the topography (contact height) and symmetry per chip of wafers
  - Jupyter script to compare errors and contact resistance for wafers
  - Python script to send updates on the status of the wafer testing

This code is intended to be used for analysis of RD53B CROC-v2 chips tested on wafers for the CMS HL-LHC upgrade and was written as part of the CMS MREFC EPO 2024 internship at Kansas State University. More information can be found at https://gitlab.cern.ch/croc_testing/croc_wlt.

Credit to Weston Schwartz (schwartzw on GitHub) for most of the contact resistance code. Special thanks to Andrew Ivanov and Wyatt Jones.

This code will regularly be updated through August 3, 2024, and may be periodically updated afterward. Contact Nat Penn at npenn@bu.edu with questions.

# How to use Wafer-Tester-Status script
If using this outside K-State, create a separate wafer testing gmail
Create a config.ini file in the Wafer-Tester-Status directory
  -   first line: [Gmail]
  -   second line: email="example@gmail.com"
  -   third line: passcode="passcode-from-gmail-app-passwords" (use the passcode from: https://myaccount.google.com/apppasswords)

Enable POP/IMAP in email settings (gmail preferred)

Make sure to also download/create the mailing list txt file (in CMS-Wafer-Testing directory) so emails can be added to be notified

Run the script from a separate terminal tab/window while testing wafers. It will end once completed

Checking status:
  - To check the status of testing, send an email to youremail@example.com with the subject "Status".
  - In the body of the email, write any of the following words (to be upated):
    - current (what chip it is currently testing)
    - last (which chip most recently completed testing, if any)
    - chips (how many chips have completed testing) 
    - time (time elapsed)
    - remaining (time remaining)
    - all (all of the above)

Mailing list:
  - To be added to the mailing list, send an email to example@gmail.com with the subject "Add".
  - To be removed from the mailing list, send an email to example@gmail.com with the subject "Remove"
  - If your email is on the mailing list, you will receive an email when the wafer has completed testing that includes the following information (to be updated):
    - Wafer name
    - Time elapsed and time completed
    - Whether the wafer was fully tested or there were errors
    - How many chips completed testing
    - Instructions for what to do next (Go to the lab and run waferanalyzer, etc.)

Allow about 5 minutes for updates 
