#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import sys
import requests
import socket
import datetime
import time
import math
import re

from db import *
from fields import *
from freebox import api_authorize, api_open_session, get_freebox
from modes import *

# Configuration
config_category = 'freebox'  # 'network' would be a great alternative

app_id = 'freebox-revolution-munin'  # Script legacy name. Changing this would break authentication
app_name = 'Freebox-OS-munin'
app_version = '1.0.0'
device_name = socket.gethostname()


parser = argparse.ArgumentParser()
parser.add_argument('arg', nargs='?')
parser.add_argument('--mode', default=__file__.split('/')[-1])  # Mode, determined by symlink name
args = parser.parse_args()

# Freebox authorization
if args.arg == 'authorize':
    api_authorize(app_id, app_name, app_version, device_name)

# Mode, determined by symlink name
mode = args.mode

if mode not in modes:
    print('Unknown mode {}'.format(mode))
    print('Accepted modes are {}'.format(', '.join(modes)))
    sys.exit(1)


# From https://github.com/yhat/rodeo/issues/90#issuecomment-98790197
def slugify(text):
    return re.sub(r'[-\s]+', '_', (re.sub(r'[^\w\s-]', '', text).strip().lower()))


def call_api(uri, params=None):
    # Build request
    r = requests.get(uri, params=params, headers={
        'X-Fbx-App-Auth': freebox.session_token
    })
    r_json = r.json()

    if not r_json['success']:
        if r_json['error_code'] == 'auth_required':
            # Open session and try again
            api_open_session(freebox, app_id)
            return call_api(uri, params)
        else:
            # Unknown error (http://dev.freebox.fr/sdk/os/login/#authentication-errors)
            print('Unknown RRD API error "{}": {}'.format(
                r_json['error_code'],
                r_json['msg']
            ))
            sys.exit(1)

    return r_json['result']


def get_connected_disks():
    return call_api(freebox.get_api_call_uri('storage/disk/'))


def query_storage_data():
    disks = get_connected_disks()

    for disk in disks:
        for partition in disk.get('partitions'):
            slug = slugify(partition.get('label'))

            free_bytes = partition.get('free_bytes')
            used_bytes = partition.get('used_bytes')

            percent = used_bytes * 100 / (free_bytes+used_bytes)
            print('{}.value {}'.format(slug, round(percent, 2)))


def query_xdsl_errors():
    data = call_api(freebox.get_api_call_uri('connection/xdsl/'))

    for kind in ['down', 'up']:
        for field in get_fields(mode):
            field_slug = '{}_{}'.format(field, kind)
            print('{}.value {}'.format(field_slug, data.get(kind).get(field)))


def query_rrd_data():
    # Load graph info
    fields = get_fields(mode)
    db = get_db(fields[0])

    # Compute date_start & date_end
    now = datetime.datetime.now()  # math.ceil(time.time())
    now = now.replace(second=0, microsecond=0)
    date_end = now.replace(minute=now.minute - now.minute % 5)  # Round to lowest 5 minutes
    date_start = now - datetime.timedelta(minutes=5)  # Remove 5 minutes from date_end
    date_end_timestamp = math.ceil(time.mktime(date_end.timetuple()))
    date_start_timestamp = math.ceil(time.mktime(date_start.timetuple()))

    data = call_api(freebox.get_api_call_uri('rrd/'), {
        'db': db,
        'fields': fields,
        'date_start': date_start_timestamp,
        'date_end': date_end_timestamp
    })['data']

    # Sum up data
    sums = {}
    for timed_data in data:
        for key, value in timed_data.items():
            if key not in fields:  # Ignore "time" and other unused values
                continue

            if key not in sums.keys():
                sums[key] = 0

            if mode == mode_xdsl:
                value /= 10

            # When combining upload+download on the same graph, download should be negative
            if key in [field_rate_down, field_bw_down, field_tx1, field_tx2, field_tx3, field_tx4]:
                value *= -1

            sums[key] += value

    # Get average from these sums
    for key, value in sums.items():
        value /= len(data)

        # Depending on field, either round or ceil value
        if mode == mode_temp:
            value = round(value, 2)
        elif mode == mode_xdsl:
            value = round(value, 1)
        else:
            value = round(value)

        sums[key] = value

    for key, value in sums.items():
        print('{}.value {}'.format(key, value))


freebox = get_freebox()
if freebox is None:
    print('Could not load Freebox from saved state.')
    sys.exit(1)

if args.arg == 'config':
    print('graph_category {}'.format(config_category))

    if mode == 'freebox-traffic':
        print('graph_title Freebox traffic')
        print('graph_vlabel byte in (-) / out (+) per second')
        print('rate_up.label Up traffic (byte/s)')
        print('rate_up.draw AREA')
        print('rate_up.colour F44336')
        print('bw_up.label Up bandwidth (byte/s)')
        print('bw_up.draw LINE')
        print('bw_up.colour 407DB5')
        print('rate_down.label Down traffic (byte/s)')
        print('rate_down.draw AREA')
        print('rate_down.colour 8BC34A')
        print('bw_down.label Down bandwidth (byte/s)')
        print('bw_down.draw LINE')
        print('bw_down.colour 407DB5')
    elif mode == 'freebox-temp':
        print('graph_title Freebox temperature')
        print('graph_vlabel temperature in C')
        print('cpum.label CPUM')
        print('cpum.colour EDC240')
        print('cpum.warning 80')
        print('cpum.critical 90')
        print('cpub.label CPUB')
        print('cpub.colour AFD8F8')
        print('cpub.warning 80')
        print('cpub.critical 90')
        print('sw.label SW')
        print('sw.colour CB4B4B')
        print('sw.warning 60')
        print('sw.critical 70')
        print('hdd.label HDD')
        print('hdd.colour 4DA74D')
        print('hdd.warning 55')
        print('hdd.critical 65')
    elif mode == 'freebox-xdsl':
        print('graph_title xDSL')
        print('graph_vlabel xDSL noise margin (dB)')
        print('snr_up.label Up')
        print('snr_up.colour CB4B4B')
        print('snr_down.label Down')
        print('snr_down.colour 4DA74D')
    elif mode == 'freebox-xdsl-errors':
        print('graph_title xDSL errors')
        print('graph_vlabel xDSL errors since last restart')
        print('graph_args --lower-limit 0')

        for kind in ['down', 'up']:
            for field in get_fields(mode):
                field_slug = '{}_{}'.format(field, kind)
                print('{}.label {}'.format(field_slug, kind.title() + ' ' + xdsl_errors_fields_descriptions.get(field)))
                print('{}.min 0'.format(field_slug))
                print('{}.draw LINE'.format(field_slug))
    elif mode.startswith('freebox-switch'):
        switch_index = mode[-1]
        print('graph_title Switch port #{} traffic'.format(switch_index))
        print('graph_vlabel byte in (-) / out (+) per second')
        print('rx_{}.label Up (byte/s)'.format(switch_index))
        print('rx_{}.draw AREA'.format(switch_index))
        print('rx_{}.colour F44336'.format(switch_index))
        print('tx_{}.label Down (byte/s)'.format(switch_index))
        print('tx_{}.draw AREA'.format(switch_index))
        print('tx_{}.colour 8BC34A'.format(switch_index))
    elif mode == 'freebox-df':
        print('graph_title Disk usage in percent')
        print('graph_args --lower-limit 0 --upper-limit 100')
        print('graph_vlabel %')

        disks = get_connected_disks()
        for disk in disks:
            for partition in disk.get('partitions'):
                name = partition.get('label')
                slug = slugify(name)

                if partition.get('internal'):
                    name += ' (interne)'

                print('{}.min 0'.format(slug))
                print('{}.max 100'.format(slug))
                print('{}.warning 85'.format(slug))
                print('{}.critical 95'.format(slug))
                print('{}.label {}'.format(slug, name))
                print('{}.draw LINE'.format(slug))

    sys.exit(0)


# Query data
if mode == mode_df:
    query_storage_data()
elif mode == mode_xdsl_errors:
    query_xdsl_errors()
else:
    query_rrd_data()
