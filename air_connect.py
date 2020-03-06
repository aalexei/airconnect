#!/usr/bin/env python3

import argparse, subprocess
import plistlib
import urllib.request
import urllib.parse
import pprint
from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
import socket
from time import sleep
import json

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

#urlGC = 'http://{}:8008/ssdp/device-desc.xml'.format(ip)
#urlGC = 'http://{}:8008/setup/eureka_info?options=detail'.format(ip)
urlGC = 'http://{}:8008/setup/eureka_info'.format(ip)

with urllib.request.urlopen(urlGC) as f:
    info_json = f.read()

info_gc = json.loads(info_json)
print(info_gc)
print()

# XXX
# pprint.pprint(plist)
# print()


# features seems to be hex of 'features' int in displays and general
f1 = hex(int(plist['features'])).upper()
f2 = hex(int(plist['displays'][0]['features'])).upper()

# TODO mac genegated plist is not being decoded properly!
# pi key it sometimes missing

paramsAP = {
    'deviceid':plist['deviceID'],
    'flags':hex(plist['statusFlags']), # used?
    'model':plist['model'],
    'pk':plist['pk'], # used?
    'srcvers':plist['sourceVersion'],
    'vv':plist['vv'], # used?
    'features':'{},{}'.format(f1,f2), # order matters
}

if 'pi' in plist:
    paramsAP['pi'] = plist['pi']

infoAP = ServiceInfo(
        type_="_airplay._tcp.local.",
        name="{name}._airplay._tcp.local.".format(**plist),
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties=paramsAP,
)

paramsGC = {
    'id':info_gc['ssdp_udn'],
    'fn':info_gc['name'],
    #'md':'Chromcast Ultra',
    #'st':0,
    #'ve':'05',
    #'ca':4101,
    'bs':info_gc['hotspot_bssid'],
    #'rm':'',
    #'rs':'',
}

infoGC = ServiceInfo(
        type_="_googlecast._tcp.local.",
        name="{name}._googlecast._tcp.local.".format(**plist),
        addresses=[socket.inet_aton(ip)],
        port=8009,
        properties=paramsGC,
)
print(infoAP)
print(infoGC)

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
