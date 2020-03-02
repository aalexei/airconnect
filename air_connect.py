#!/usr/bin/env python3

import argparse, subprocess
import plistlib
import urllib.request
import urllib.parse
import pprint
from zeroconf import ServiceBrowser, Zeroconf, IPVersion, ServiceInfo
import socket
from time import sleep


parser = argparse.ArgumentParser(description='Connect to AirServer')
parser.add_argument('ip', metavar='IP-address', help='IP address of server')
parser.add_argument('-p', dest='port', metavar='port', type=int, default=5000, help='port (default:5000)')

args = parser.parse_args()

ip = args.ip
port = args.port

url = 'http://{}:{}/info?txtAitPlay'.format(ip,port)

with urllib.request.urlopen(url) as f:
    pl = f.read()

# response is Apple binary list
plist = plistlib.loads(pl)

# XXX
# pprint.pprint(plist)
# print()

# pi key it sometimes missing and looks like a uuid
# guessing it's an id for the screen
if 'pi' in plist:
    pivalue = plist['pi']
else:
    pivalue = plist['displays'][0]['uuid']


# features seems to be hex of 'features' int in displays and general
f1 = hex(int(plist['displays'][0]['features'])).upper()
f2 = hex(int(plist['features'])).upper()

# TODO mac genegated plist is not being decoded properly!


params = {
    'deviceid':plist['deviceID'],
    'flags':hex(plist['statusFlags']),
    'model':plist['model'],
    'pk':plist['pk'],
    'pi':pivalue,
    'srcvers':plist['sourceVersion'],
    'vv':plist['vv'],
    'features':'{},{}'.format(f1,f2),
}

print(plist['name'])
print(params)

# following parameters work
params = {
    'deviceid':'38:C9:86:3F:AF:B5',
    'flags':'0x4',
    'model':'AppleTV5,3',
    'pi':'1FC82B97-F4ED-43CB-AE17-03C8F4D6108F',
    'pk':'d3a29c415d4b2c3aa68c043dcd7ed880c7f702313ae05044772e743076fb5acc',
    'srcvers':'220.68',
    'vv':'2',
    'features':'0x4A7FFFF7,0xE',
}

info = ServiceInfo(
        type_="_airplay._tcp.local.",
        name="{name}._airplay._tcp.local.".format(**plist),
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties=params,
        #server="{name}.local.".format(**plist),
    )

zeroconf = Zeroconf(ip_version=IPVersion.V4Only)
print("Registration of a service, press Ctrl-C to exit...")
zeroconf.register_service(info)
try:
    while True:
        sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    print("Unregistering...")
    zeroconf.unregister_service(info)
    zeroconf.close()