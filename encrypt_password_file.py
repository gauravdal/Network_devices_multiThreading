from simplecrypt import encrypt, decrypt
from pprint import pprint
import csv
import json

dc_in_filename = input('\nInput CSV filename (device-creds) :    ') or 'device-creds'
key            = input(  'Encryption key (cisco)        :  ') or 'cisco'

#reading device credentials

with open(dc_in_filename,'r') as dc_in:
    device_creds_reader = csv.reader(dc_in)
    device_creds_list = [device for device in device_creds_reader]

#printing the device crediantials list
print('printing the device credentials....\n\n')
pprint(device_creds_list)

encrypted_dc_out_filename = input('\n enter the name of the output encrypted file:   ') or 'encrypted-device-creds'

#Encrypting the device credentials with key
with open(encrypted_dc_out_filename,'wb') as dc_out:
    dc_out.write(encrypt(key, json.dumps(device_creds_list)))

print('I have encrypted the file')

print('\n...Geting credentials....\n')
with open(encrypted_dc_out_filename,'rb') as device_creds_file:
    device_creds_json = decrypt(key, device_creds_file.read())

device_creds_list = json.loads( device_creds_json.decode('utf-8'))
pprint(device_creds_list)
#converting to dictionary....!

device_creds = {dev[0]:dev for dev in device_creds_list}
pprint(device_creds)
