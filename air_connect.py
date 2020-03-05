#!/usr/bin/env python3

import argparse, subprocess
import plistlib
import urllib.request
import urllib.parse
import pprint
from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
import socket
from time import sleep


parser = argparse.ArgumentParser(description='Connect to AirServer')
parser.add_argument('ip', metavar='IP-address', help='IP address of server')
parser.add_argument('-p', dest='port', metavar='port', type=int, default=7000, help='port (default:7000)')

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


# features seems to be hex of 'features' int in displays and general
f1 = hex(int(plist['features'])).upper()
f2 = hex(int(plist['displays'][0]['features'])).upper()

# TODO mac genegated plist is not being decoded properly!
# pi key it sometimes missing

params = {
    'deviceid':plist['deviceID'],
    'flags':hex(plist['statusFlags']), # used?
    'model':plist['model'],
    'pk':plist['pk'], # used?
    'srcvers':plist['sourceVersion'],
    'vv':plist['vv'], # used?
    'features':'{},{}'.format(f1,f2), # order matters
}

if 'pi' in plist:
    params['pi'] = plist['pi']

infoAP = ServiceInfo(
        type_="_airplay._tcp.local.",
        name="{name}._airplay._tcp.local.".format(**plist),
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties=params,
)

infoGC = ServiceInfo(
        type_="_googlecast._tcp.local.",
        name="{name}._googlecast._tcp.local.".format(**plist),
        addresses=[socket.inet_aton(ip)],
        port=8008,
        #properties=params,
)
print(infoAP, infoGC)

zeroconf = Zeroconf()
zeroconf.register_service(infoAP)
zeroconf.register_service(infoGC)
print("Registration of a service, press Ctrl-C to exit...")
try:
    while True:
        sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    print("Unregistering...")
    zeroconf.unregister_service(infoAP)
    zeroconf.unregister_service(infoGC)
    zeroconf.close()
