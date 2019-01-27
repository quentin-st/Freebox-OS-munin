#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" This script provides munin scripts for Freebox OS stats.
 Freebox Revolution & Freebox 4K are supported for the following stats:
 - traffic,
 - temp,
 - fan_speed,
 - xdsl,
 - xdsl_errors,
 - switch1,
 - switch2,
 - switch3,
 - switch4,
 - df
 - transmission-tasks
 - transmission-traffic """

import argparse
import sys
import datetime
import time
import math

from db import *
from fields import *
from freebox import app_version, api_authorize, get_freebox
from modes import *
from util import *

###############
# Configuration
###############
MUNIN_CATEGORY = 'freebox'  # 'network' would be a great alternative


__author__ = 'Quentin Stoeckel'
__copyright__ = 'Copyright 2016, Quentin Stoeckel and contributors'
__credits__ = ['Contributors at https://github.com/chteuchteu/Freebox-OS-munin/graphs/contributors']

__license__ = 'gpl-v2'
__version__ = app_version
__maintainer__ = "chteuchteu"
__email__ = 'stoeckel.quentin@gmail.com'
__status__ = 'Production'


parser = argparse.ArgumentParser()
parser.add_argument('arg', nargs='?')
parser.add_argument('--mode', default=__file__.split('/')[-1])  # Mode, determined by symlink name
args = parser.parse_args()


def print_config():
    print('graph_category {}'.format(MUNIN_CATEGORY))

    if mode == mode_traffic:
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
    elif mode == mode_temp:
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
    elif mode == mode_fan_speed:
        print('graph_title Freebox fan speed')
        print('graph_vlabel rpm')
        print('fan_speed.label Internal fan speed')
        print('fan_speed.colour 50A850')
        print('fan_speed.critical 1:')
    elif mode == mode_xdsl:
        print('graph_title xDSL')
        print('graph_vlabel xDSL noise margin (dB)')
        print('snr_up.label Up')
        print('snr_up.colour CB4B4B')
        print('snr_down.label Down')
        print('snr_down.colour 4DA74D')
    elif mode == mode_xdsl_errors:
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
    elif mode == mode_df:
        print('graph_title Disk usage in percent')
        print('graph_args --lower-limit 0 --upper-limit 100')
        print('graph_vlabel %')

        disks = freebox.api_get_connected_disks()
        for disk in disks:
            for partition in disk.get('partitions'):
                name = partition.get('label')
                slug = slugify(name)

                name += " (" + disk.get('type') + ")"

                print('{}.min 0'.format(slug))
                print('{}.max 100'.format(slug))
                print('{}.warning 85'.format(slug))
                print('{}.critical 95'.format(slug))
                print('{}.label {}'.format(slug, name))
                print('{}.draw LINE'.format(slug))
    elif mode == mode_hddspin:
        print('graph_title Spinning status for Freebox disks')
        print('graph_args --lower-limit 0 --upper-limit 1')
        print('graph_vlabel Disk state (active/sleep)')

        disks = freebox.api_get_connected_disks()
        for disk in disks:
            name = disk.get('display_name')
            slug = disk.get('slug')

            print('{}.min 0'.format(slug))
            print('{}.max 1'.format(slug))
            print('{}.label {}'.format(slug, name))
            print('{}.draw AREASTACK'.format(slug))
            print('{}_down.min 0'.format(slug))
            print('{}_down.max 1'.format(slug))
            print('{}_down.label {} - OFF'.format(slug, name))
            print('{}_down.draw AREASTACK'.format(slug))
            print('{}_down.colour ffffff'.format(slug))
    elif mode == mode_transmission_tasks:
        print('graph_title Transmission tasks stats')
        print('graph_args --lower-limit 0')
        print('graph_vlabel #')

        for field in get_fields(mode):
            print('{}.min 0'.format(field))
            print('{}.label Number of {} tasks'.format(field, field.split('_')[-1]))
            print('{}.draw AREASTACK'.format(field))
    elif mode == mode_transmission_traffic:
        print('graph_title Transmission traffic')
        print('graph_vlabel byte in (-) / out (+) per second')
        print('tx_rate.label Up (byte/s)')
        print('tx_rate.draw AREA')
        print('tx_rate.colour F44336')
        print('tx_throttling.label Up throttling (byte/s)')
        print('tx_throttling.draw LINE')
        print('tx_throttling.colour 407DB5')
        print('rx_rate.label Down (byte/s)')
        print('rx_rate.draw AREA')
        print('rx_rate.colour 8BC34A')
        print('rx_throttling.label Down throttling (byte/s)')
        print('rx_throttling.draw LINE')
        print('rx_throttling.colour 407DB5')


def query_data():
    if mode == mode_df:
        query_storage_data()
    elif mode == mode_hddspin:
        query_storagespin_data()
    elif mode == mode_xdsl_errors:
        query_xdsl_errors()
    elif mode == mode_transmission_tasks:
        query_transmission_tasks_data()
    elif mode == mode_transmission_traffic:
        query_transmission_traffic_data()
    else:
        query_rrd_data()


def query_storage_data():
    disks = freebox.api_get_connected_disks()

    for disk in disks:
        for partition in disk.get('partitions'):
            slug = slugify(partition.get('label'))

            free_bytes = partition.get('free_bytes')
            used_bytes = partition.get('used_bytes')

            percent = used_bytes * 100 / (free_bytes+used_bytes)
            print('{}.value {}'.format(slug, round(percent, 2)))


def query_storagespin_data():
    disks = freebox.api_get_connected_disks()

    for disk in disks:
        slug = disk.get('slug')
        state = disk.get('spinning')

        if state is True:
            print('{}.value 1'.format(slug))
            print('{}_down.value 0'.format(slug))
        else:
            print('{}.value 0'.format(slug))
            print('{}_down.value 1'.format(slug))


def query_xdsl_errors():
    data = freebox.api('connection/xdsl/')

    for kind in ['down', 'up']:
        for field in get_fields(mode):
            field_slug = '{}_{}'.format(field, kind)
            print('{}.value {}'.format(field_slug, data.get(kind).get(field)))


def query_transmission_tasks_data():
    data = freebox.api('downloads/stats/')

    for field in get_fields(mode):
        print('{}.value {}'.format(field, data.get(field)))


def query_transmission_traffic_data():
    data = freebox.api('downloads/stats/')

    # When combining upload+download on the same graph, download should be negative
    print('tx_rate.value {}'.format(data.get(field_tx_rate)))
    print('tx_throttling.value {}'.format(data.get('throttling_rate').get('tx_rate')))
    print('rx_rate.value {}'.format(-1 * data.get(field_rx_rate)))
    print('rx_throttling.value {}'.format(-1 * data.get('throttling_rate').get('rx_rate')))


def query_rrd_data():
    # Load graph info
    rrd_fields = get_fields(mode)
    db = get_db(rrd_fields[0])

    # Compute date_start & date_end
    now = datetime.datetime.now()  # math.ceil(time.time())
    now = now.replace(second=0, microsecond=0)
    date_end = now.replace(minute=now.minute - now.minute % 5)  # Round to lowest 5 minutes
    date_start = date_end - datetime.timedelta(minutes=5)  # Remove 5 minutes from date_end
    date_end_timestamp = math.ceil(time.mktime(date_end.timetuple()))
    date_start_timestamp = math.ceil(time.mktime(date_start.timetuple()))

    data = freebox.api('rrd/', {
        'db': db,
        'fields': rrd_fields,
        'date_start': date_start_timestamp,
        'date_end': date_end_timestamp
    })['data']

    # Sum up data
    sums = {}
    for timed_data in data:
        for key, value in timed_data.items():
            if key not in rrd_fields:  # Ignore "time" and other unused values
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


# Freebox authorization
if args.arg == 'authorize':
    exit_code = api_authorize()
    sys.exit(exit_code)

# Mode, determined by symlink name
mode = args.mode

if mode not in modes and mode != 'all':
    print('Unknown mode {}'.format(mode))
    print('Accepted modes are {}'.format(', '.join(modes)))
    sys.exit(1)

freebox = get_freebox()
if freebox is None:
    print('Could not load Freebox from saved state.')
    sys.exit(1)

if args.arg == 'config':
    print_config()
    sys.exit(0)

# Great for testing
if mode == 'all':
    for m in modes:
        mode = m
        print_config()
        query_data()

    sys.exit(0)

# Query data
query_data()
