#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
import requests
import socket
import datetime

from db import *
from fields import *
from freebox import api_authorize, api_open_session, get_freebox
from modes import *

# Configuration
config_category = 'freebox'  # 'network' would be a great alternative

# Useful for development
force_auth = False
force_config = False
force_mode = False
forced_mode = mode_traffic

app_id = 'freebox-revolution-munin'
app_name = 'Freebox-Revolution-munin'
app_version = '1.0.0'
device_name = socket.gethostname()


# Munin config mode
parser = argparse.ArgumentParser()
parser.add_argument('arg', nargs='?')
args = parser.parse_args()

# Freebox authorization
if args.arg == 'authorize' or force_auth:
    api_authorize(app_id, app_name, app_version, device_name)

# Mode, determined by symlink name
mode = __file__.split('/')[-1]
if force_mode:
    mode = forced_mode

if mode not in modes:
    print('Unknown mode {}'.format(mode))
    print('Accepted modes are {}'.format(', '.join(modes)))
    sys.exit(1)


if args.arg == 'config' or force_config:
    print('graph_category {}'.format(config_category))

    if mode == 'freebox-traffic':
        print('graph_title Freebox traffic')
        print('graph_vlabel byte in (-) / out (+) per second')
        print('rate_up.label Up traffic (byte/s)')
        print('rate_up.draw AREA')
        print('bw_up.label Up bandwidth (byte/s)')
        print('bw_up.draw LINE')
        print('rate_down.label Down traffic (byte/s)')
        print('rate_down.draw AREA')
        print('bw_down.label Down bandwidth (byte/s)')
        print('bw_down.draw LINE')
    elif mode == 'freebox-temp':
        print('graph_title Freebox temperature')
        print('graph_vlabel temperature in °C')
        print('cpum.label CPUM')
        print('cpub.label CPUB')
        print('sw.label SW')
        print('hdd.label HDD')
    elif mode == 'freebox-xdsl':
        print('graph_title xDSL')
        print('graph_vlabel xDSL noise margin (dB)')
        print('snr_up.label Up')
        print('snr_down.label Down')
    elif mode.startswith('freebox-switch'):
        switch_index = mode[:-1]
        print('graph_title Switch port #{} traffic'.format(switch_index))
        print('graph_vlabel byte in (-) / out (+) per second')
        print('tx_{}.label Up (byte/s)'.format(switch_index))
        print('tx_{}.draw AREA'.format(switch_index))
        print('rw_{}.label Down (byte/s)'.format(switch_index))
        print('rw_{}.draw AREA'.format(switch_index))

    sys.exit(0)


# Query data
freebox = get_freebox()
if freebox is None:
    print('Could not load Freebox from saved state.')
    sys.exit(1)

api_open_session(freebox, app_id)

# Load graph info
uri = freebox.get_api_call_uri() + 'rrd/'
fields = get_fields(mode)
db = get_db(fields[0])

# Compute date_start & date_end
now = datetime.datetime.now()  # math.ceil(time.time())
now = now.replace(second=0, microsecond=0)
date_end = now.replace(minute=now.minute - now.minute % 5)  # Round to lowest 5 minutes
date_start = now - datetime.timedelta(minutes=5)  # Remove 5 minutes from date_end

params = {
    'db': db,
    'fields': fields,
    'date_start': date_start,
    'date_end': date_end
}

if db == db_temp:
    params['precision'] = '10'

# Build request
r = requests.get(uri, params=params, headers={
    'X-Fbx-App-Auth': freebox.session_token
})
r_json = r.json()

# Sum up data
sums = {}
for timed_data in r_json['result']['data']:
    for key, value in timed_data.items():
        if key not in fields:  # Ignore "time" and other unused values
            continue

        if key not in sums.keys():
            sums[key] = 0

        sums[key] += value

for key, value in sums.items():
    print('{}.value {}'.format(key, value))
