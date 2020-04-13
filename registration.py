#!/usr/bin/env python
# -*- coding: utf8 -*-
 
import RPi.GPIO as GPIO
from mfrc522 import MFRC522
import signal
import time
import csv
 
continue_reading = True 
duplicate = False
 
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
        
        # Check database if RFID exists so we avoid duplicates
        with open('registered_cars.csv', 'r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=';')
            line_count = 1
            
            for row in csv_reader:
                rfid_id = row[0]
                
                if line_count > 0:
                    if str(uid) == str(rfid_id):
                        print ("DUPLICATE RFID DETECTED:", row)
                        duplicate = True
                        break
                    else:
                        duplicate = False
                        print ("no duplicate")
                line_count += 1

        if duplicate == False:
            print ("RFID DETECTED:", uid)
            # Declare variables
            saved = 0
            plates = input('Enter license plates: ')
            owner = input('Enter owner: ')
            registered = 1
        
            # Open CSV file and compare the readed card UID with entries from the CSV file
            with open('registered_cars.csv', 'a') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter=';')
                row = [uid, plates, owner, registered]
                csv_writer.writerow(row)
                print ("SAVED RECORD:", row)
                
