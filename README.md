# CMS-Wafer-Testing
Contents of this project:
  - Jupyter and python scripts to analyze and compare the frequency of errors in wafer testing
  - Jupyter and python scripts to analyze the contact resistance over time of a wafer test
  - Jupyter and python scripts to map the topography (contact height) and symmetry per chip of wafers
  - Jupyter script to compare errors and contact resistance for wafers
  - Python script to send updates on the status of the wafer testing

This code is intended to be used for analysis of RD53B chips tested on wafers for the CMS HL-LHC upgrade and was written as part of the CMS MREFC EPO 2024 internship at Kansas State University. More information can be found at https://gitlab.cern.ch/croc_testing/croc_wlt.

Credit to Weston Schwartz (schwartzw on GitHub) for most of the contact resistance code. Special thanks to Andrew Ivanov and Wyatt Jones.

Contact Nat Penn at npenn@bu.edu with questions.

# How to use Wafer-Tester-Status script
Create a config.ini file
  -   first line: [Gmail]
  -   second line: email="youremail@example.com"
  -   third line: passcode="passcode-from-gmail-app-passwords"

Enable POP/IMAP in email settings (gmail preferred)

Make sure to also download/create the mailing list txt file so emails cana be added to be notified

Run the script from a separate terminal tab/window while testing wafers

Checking status:
  - To check the status of testing, send an email to youremail@example.com with the subject "Status".
  - In the body of the email, write any of the following words (to be upated):
    - current (what chip it is currently testing)
    - last (which chip most recently completed testing, if any)
    - time (time elapsed)
    - chips (how many chips have completed testing) 

Mailing list:
  - To be added to the mailing list, send an email to youremail@example.com with the subject "Add".
  - To be removed from the mailing list, send an email to youremail@example.com with the subject "Remove"
  - If your email is on the mailing list, you will receive an email when the wafer has completed testing that includes the following information (to be updated):
    - Wafer name
    - Time elapsed and time completed
    - Whether the wafer was fully tested or there were errors
    - How many chips completed testing
    - Instructions for what to do next (Go to the lab and run waferanalyzer, etc.)

Allow about 5 minutes for updates 
