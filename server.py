import json
import requests
import os
import subprocess

interval = 5

# Run TSSChecker to save blobs
def tsschecker(model, ecid, version):
    result = subprocess.check_output([os.path.join(os.getcwd(), "tsschecker"), "-d%s" % model, "-e%s" % ecid, "-i%s" % version, "-s"])
    if ("Saved shsh blobs!" in str(result)):
        print("Success!")
    else:
        print("Failed to fetch blobs.")
    
    # Scan for output file
    contents = os.listdir(os.path.join(os.getcwd()))
    name = "%s_%s_%s" % (ecid, model, version)
    for filename in contents:
        if (name in filename):
            os.rename(os.path.join(os.getcwd(), filename), os.path.join(os.getcwd(), "blobs", ecid, version + ".shsh2"))
            print ("Renamed '%s' to '%s'." % (filename, name))

# Check if blobs folder exists- if it doesn't, create it
path = os.getcwd()
print(path)

try:  
    os.mkdir(os.path.join(os.getcwd(), "blobs"))
    print("Created blobs directory.")

    devices = open("devices.json", "w+")
    devices.write("{\n}")
    devices.close()
    print("Created devices.json.")
except FileExistsError:
    pass

try:
    with open('devices.json') as json_file:  
        data = json.load(json_file)
        for p in data['people']:
            print('Name: ' + p['name'])
            print('Website: ' + p['website'])
            print('From: ' + p['from'])
except:
    print("Error reading devices file.")


firmwares = requests.get("https://api.ipsw.me/v2.1/firmwares.json/condensed").content
firmwares = json.loads(firmwares)

#for key in firmwares['devices'].keys():
    #print(key)

# Read devices.json
devices = open("devices.json", "r").read()
parsed = json.loads(devices)

for device in parsed['devices']:
    print("Fetching for %s (%s ECID: %s)." % (device['name'], device['model'], device['ecid']))

    # Check if device model exists
    if (not device['model'] in firmwares['devices']):
        print("Device model %s does not exist." % device['model'])
        continue

    if (not os.path.isdir(os.path.join(os.getcwd(), "blobs", device['ecid']))):
        try:  
            os.mkdir(os.path.join(os.getcwd(), "blobs", device['ecid']))
        except FileExistsError:
            continue

    signed = []

    # Fetch currently signed versions
    for version in firmwares['devices'][device['model']]['firmwares']:
        if (not version['signed']):
            #print("Version %s is not signed." % version['version'])
            continue
        
        signed.append(version['version'])
        print("iOS %s is being signed for %s." % (version['version'], device['model']))
    
    # Check if blob for version exists. If not, download and save.
    for blob in signed:
        contents = os.listdir(os.path.join(os.getcwd(), "blobs", device['ecid']))
        if (blob + ".shsh2" in contents):
            print("SHSH blob for version %s already exists." % blob)
            continue
        
        # Run TTSChecker in a new thread to save the blob
        tsschecker(device['model'], device['ecid'], blob)