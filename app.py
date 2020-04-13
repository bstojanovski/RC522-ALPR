#!/usr/bin/env python
# -*- coding: utf8 -*-

import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import signal
import time
import csv
import shlex, subprocess
import requests
import base64
import json

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read(signal,frame):
    global continue_reading
    print ("Ctrl+C captured, ending read.")
    continue_reading = False
    GPIO.cleanup()
 
# Hook the SIGINT
signal.signal(signal.SIGINT, end_read)
 
# Create an object of the class MFRC522
MIFAREReader = MFRC522()
 
# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    
    # Get the UID of the card
    (status,uid) = MIFAREReader.MFRC522_Anticoll()
 
    # If we have the UID, continue
    if status == MIFAREReader.MI_OK:
        
        # Select the scanned tag
        MIFAREReader.MFRC522_SelectTag(uid)
        
        # Declare variables
        saved = 0
        plates = ""
        owner = ""
        registered = 0
    
        #Open CSV file and compare the readed card UID with entries from the CSV file
        with open('registered_cars.csv') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 1
            
            for row in csv_reader:
                rfid_id = row[0]
                rfid_plates = row[1]
                rfid_owner = row[2]
                rfid_registered = row[3]
                        
                if str(uid) == str(rfid_id):
                        saved = 1
                        plates = rfid_plates
                        owner = rfid_owner
                        registered = rfid_registered
        
        # Check to see if the card is authorized
        if saved:
            fswebcam_command = "fswebcam -r 1200x720 -S 20 --no-banner --quiet slika.jpeg"
            args = shlex.split(fswebcam_command)
            fswebcam_p = subprocess.Popen(args)
            
            alpr_command = "alpr -c eu -j slika.jpeg"
            with open('data.json', "w") as outfile:
                subprocess.call(alpr_command, shell=True, stdout=outfile)
                
            cpdata_command = "cp data.json /var/www/html/ && cp slika.jpeg /var/www/html/"
            subprocess.call(cpdata_command, shell=True)
            
            print ("\n\u001b[36m======== RFID INFO ========")
            print ("Plates:", plates)
            print ("Owner:", owner)
            print ("Registration:", registered)
            
            with open('data.json', 'r') as infile:
                content = infile.read()
                results = json.loads(content)['results']
                print ("\n\u001b[33m-------- ALPR DATA --------")
                if results:
                    json_data = results[0]
                    print ("Plates:", json_data['plate'])
                    print ("Confidence:", json_data['confidence'])
                    
                    if json_data['plate'] == plates:
                        print ("\n\n\u001b[32m=== MATCHING PLATES ===\n\n")
                    else:
                        print ("\n\n\u001b[31m=== PLATES NOT MATCHING! ===\n\n")
                else:
                    print ("\u001b[31mNO DATA FOUND")
        else:
            print("\u001b[31mERROR: Unknown RFID detected!")

