#!/usr/bin/python3
# -*- coding: utf-8 -*-

import json
import argparse
import sys
import requests
import socket

from db import *
from fields import *
from freebox import api_authorize, api_open_session, get_freebox
from modes import *


# Useful for development
force_auth = False
force_config = False
force_mode = True
forced_mode = mode_traffic

app_id = 'freebox-revolution-munin'
app_name = 'Freebox-Revolution-munin'
app_version = '1.0.0'
device_name = socket.gethostname()


# Munin config mode
parser = argparse.ArgumentParser()
parser.add_argument('config', nargs='?')
parser.add_argument('freebox_auth', nargs='?')
args = parser.parse_args()

# Freebox authorization
if args.freebox_auth == 'freebox_auth' or force_auth:
    api_authorize(app_id, app_name, app_version, device_name)

# Mode: either '', ... determined by symlink name
mode = __file__.split('/')[-1]
if force_mode:
    mode = forced_mode

if mode not in modes:
    print('Unknown mode {}'.format(mode))
    print('Accepted modes are {}'.format(', '.join(modes)))
    sys.exit(1)


if args.config == 'config' or force_config:
    if mode == 'freebox-traffic':
        print('graph_title Freebox traffic')
        print('graph_vlabel bits in (-) / out (+) per second')
        print('rate_up.label Up traffic (B/s)')
        print('rate_up.draw AREA')
        print('bw_up.label Up bandwidth (B/s)')
        print('bw_up.draw LINE')
        print('rate_down.label Down traffic (B/s)')
        print('rate_down.draw AREA')
        print('bw_down.label Down bandwidth (B/s)')
        print('bw_down.draw LINE')
    elif mode == 'freebox-temp':
        print('graph_title Freebox temperature')
        print('graph_vlabel temperature in °C')
        print('graph_category network')
        print('cpum.label CPUM')
        print('cpub.label CPUB')
        print('sw.label SW')
        print('hdd.label HDD')
    elif mode == 'freebox-xdsl':
        print('graph_title xDSL')
        print('graph_vlabel xDSL noise margin (dB)')
        print('up.label Up')
        print('down.label Down')
    elif mode.startswith('freebox-switch'):
        switch_index = mode[:-1]
        print('graph_title Switch port #{} traffic'.format(switch_index))
        print('graph_vlabel bits in (-) / out (+) per second')
        print('up.label Up (B/s)')
        print('up.draw AREA')
        print('down.label Down (B/s)')
        print('down.draw AREA')

    sys.exit(0)


# Query data
freebox = get_freebox()
if freebox is None:
    print('Could not load Freebox from saved state.')
    sys.exit(1)

api_open_session(freebox, app_id)

# Load graph info
fields = get_fields(mode)

uri = freebox.get_api_call_uri() + 'rrd/'
db = get_db(fields[0])

params = {
    'db': db,
    'fields': fields,
    'date_start': 0,  # TODO
}

if db == db_temp:
    params['precision'] = '10'

# Build request
r = requests.get(uri, params=params, headers={
    'X-Fbx-App-Auth': freebox.session_token
})

print(r.json())
