from simplecrypt import encrypt, decrypt
from pprint import pprint
from netmiko import ConnectHandler
import csv
import json
from time import time
import threading

def read_devices( devices_filename):

    devices = {}    #creating dictionary for storing devices and their info

    with open(devices_filename,'r') as device_file:
        device_reader = csv.reader(device_file)
        device_list = [device for device in device_reader]

        for each_device in device_list:
            device_dict = {'ipaddr': each_device[0],
                            'type':   each_device[1],
                            'name':   each_device[2]}
            devices[device_dict['ipaddr']] = device_dict

    print('-----devices-----------------------------\n')
    pprint(devices)

    return devices

def read_devices_creds(device_creds_filename, key):

    print('\n....getting credentials....\n')
    with open( device_creds_filename, 'rb') as device_creds_file:
        device_creds_json = decrypt(key, device_creds_file.read())

        device_creds_list = json.loads(device_creds_json.decode('utf-8'))

        print('\n------device creds---------\n')
        device_creds = {dev[0]:dev for dev in device_creds_list}

        pprint(device_creds)

        return device_creds

def config_worker(device, creds):

    #---- connect to device ------#
    if device['type'] =='junos-srx' : device_type = 'juniper'
    elif device['type'] == 'cisco-ios' : device_type = 'cisco_ios'
    elif device['type'] == 'cisco-xr': device_type = 'cisco_xr'
    else:                              device_type = 'cisco_ios'  #attempt cisco ios default

    print('------ Connecting to device ={0}, username={1}, password={2}'.format(device['ipaddr'],creds[1],creds[2]))


    # ---- connect to device -----#
    session = ConnectHandler(device_type = device_type,
                             host = device['ipaddr'],
                             username = creds[1],
                             password= creds[2])

    if device_type == 'juniper':
        # ---- Use CLI command to get configuration data from device
        print('---- Getting configuration from device')
        session.send_command('configure terminal')
        config_data = session.send_command('show configuration')

    if device_type == 'cisco_ios':
        # ---- Use CLI command to get configuration data from device
        print('---- Getting configuration from device')
        config_data = session.send_command('show run')

    if device_type == 'cisco_xr':
        # ---- Use CLI command to get configuration data from device
        print('---- Getting configuration from device')
        config_data = session.send_command('show configuration running-config')

    # ---- Write out configuration information to file
    config_filename = 'config-' + device['ipaddr']  # Important - create unique configuration file name

    print('---- Writing configuration: ', config_filename)
    with open(config_filename, 'w') as config_out:
        config_out.write(config_data)

    session.disconnect()

    return


#===================== Main- configuration ===============================================================
#=========================================================================================================

devices = read_devices('devices-file')
creds = read_devices_creds('encrypted-device-creds','cisco')

starting_time = time()

#----- creating threads to access devices simuntaneously ------#

threads_list = []
for ipaddr,device in devices.items():
    print('creating thread for device: ',device)
    threads_list.append(threading.Thread(target=config_worker, args=(device,creds[ipaddr])))

print('\n------Beginning of threading -------\n')
for each_thread in threads_list:
    each_thread.start()

for each_thread in threads_list:
    each_thread.join()

print('\n\n------------ End get config sequential, elapsed time= ',time()-starting_time)