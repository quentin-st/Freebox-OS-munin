#!/usr/bin/env python3
# -*- coding: utf-8 -*-

""" This script provides munin scripts for Freebox OS stats.
 Freebox Revolution & Freebox 4K are supported for the following stats:
 - traffic,
 - temp,
 - fan-speed,
 - hddspin,
 - xdsl,
 - xdsl-errors,
 - switch1,
 - switch2,
 - switch3,
 - switch4,
 - df
 - transmission-tasks
 - transmission-traffic """

import os
import json
import argparse
import sys
import datetime
import time
import math

from db import *
from fields import *
from freebox import app_version, Freebox, FreeboxNoState
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
    elif mode.startswith('freebox-switch-bytes'):
        switch_index = mode[-1]
        print('graph_title Switch port #{} traffic'.format(switch_index))
        print('graph_scale yes')
        print('graph_vlabel bytes per second')
        print('graph_args --logarithmic')
        print('rx_good_bytes.label rx')
        print('rx_good_bytes.type COUNTER')
        print('tx_bytes.label tx')
        print('tx_bytes.type COUNTER')
    elif mode.startswith('freebox-switch-packets'):
        switch_index = mode[-1]
        print('graph_title Switch port #{} traffic'.format(switch_index))
        print('graph_scale yes')
        print('graph_vlabel packets per second')
        print('graph_args --logarithmic')
        print('rx_good_packets.label rx')
        print('rx_good_packets.type COUNTER')
        print('tx_packets.label tx')
        print('tx_packets.type COUNTER')
        print('rx_unicast_packets.label rx unicast')
        print('rx_unicast_packets.type COUNTER')
        print('tx_unicast_packets.label tx unicast')
        print('tx_unicast_packets.type COUNTER')
        print('rx_broadcast_packets.label rx broadcast')
        print('rx_broadcast_packets.type COUNTER')
        print('tx_broadcast_packets.label tx broadcast')
        print('tx_broadcast_packets.type COUNTER')
    elif mode.startswith('freebox-switch-stations'):
        switch_index = mode[-1]
        print('graph_title Switch port #{} stations'.format(switch_index))
        print('graph_vlabel #')
        print('graph_total Total')
        print('graph_args --lower-limit 0')
        stations = get_switch_stations(switch_index)
        for station in stations:
            station_safe = station.replace(" ", "_")
            print('{}.label {}'.format(station, stations[station_safe]['hostname']))
            print('{}.draw AREASTACK'.format(station_safe))
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
    elif mode == mode_connection:
        print('graph_scale yes')
        print('graph_title bytes up/down')
        print('graph_vlabel bytes in (-) / out (+) per second')
        print('bytes_down.type COUNTER')
        print('bytes_down.label bytes/s')
        print('bytes_down.graph no')
        print('bytes_up.label bytes/s')
        print('bytes_up.type COUNTER')
        print('bytes_up.negative bytes_down')
    elif mode == mode_connection_log:
        print('graph_scale yes')
        print('graph_title bytes up/down')
        print('graph_vlabel bytes per second')
        print('graph_args --logarithmic')
        print('bytes_down.type COUNTER')
        print('bytes_down.label down (bytes/s)')
        print('bytes_up.type COUNTER')
        print('bytes_up.label up (bytes/s)')
    elif mode == mode_ftth:
        print('graph_title FTTH status')
        print('graph_args --lower-limit 0 --upper-limit 1')
        print('graph_vlabel Status')
        for field in get_fields(mode):
            print('{}.min 0'.format(field))
            print('{}.max 1'.format(field))
            print('{}.label {}'.format(field, field))
            print('{}.draw AREASTACK'.format(field))
    elif mode == mode_wifi_stations:
        print('graph_title Wifi stations')
        print('graph_vlabel #')
        print('graph_total Total')
        print('graph_args --lower-limit 0')
        stations = get_wifi_stations()
        for station in stations:
            station_safe = station.replace(" ", "_")
            print('{}.label {}'.format(station_safe, station))
            print('{}.draw AREASTACK'.format(station_safe))
    elif mode == mode_wifi_bytes:
        print('graph_title Wifi bytes up/down')
        print('graph_scale yes')
        print('graph_vlabel byte in (-) / out (+) per second')
        print('rx_bytes.type COUNTER')
        print('rx_bytes.label bytes/s')
        print('rx_bytes.graph no')
        print('tx_bytes.label bytes/s')
        print('tx_bytes.type COUNTER')
        print('tx_bytes.negative rx_bytes')
    elif mode == mode_wifi_bytes_log:
        print('graph_title Wifi bytes up/down')
        print('graph_scale yes')
        print('graph_vlabel bytes per second')
        print('graph_args --logarithmic')
        print('rx_bytes.type COUNTER')
        print('rx_bytes.label down (bytes/s)')
        print('tx_bytes.type COUNTER')
        print('tx_bytes.label up (bytes/s)')


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
    elif mode in [mode_connection, mode_connection_log]:
        query_connection()
    elif mode == mode_ftth:
        query_ftth()
    elif mode.startswith('freebox-switch-stations'):
        switch_index = mode[-1]
        query_switch_stations(switch_index)
    elif mode.startswith('freebox-switch-'):
        switch_index = mode[-1]
        mode2 = mode[:-1]
        query_switch(switch_index, mode2)
    elif mode == mode_wifi_stations:
        query_wifi_stations()
    elif mode in [mode_wifi_bytes, mode_wifi_bytes_log]:
        query_wifi_bytes()
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


def query_ftth():
    data = freebox.api('connection/ftth/')

    for field in get_fields(mode):
        if data.get(field):
            value = 1
        else:
            value = 0
        print('{}.value {}'.format(field, value))


def get_wifi_stations():
    data = freebox.api('wifi/ap/0/stations/')

    # the filename is something like
    # /var/lib/munin-node/plugin-state/nobody/freebox-wifi-stations-
    wifi_filename = os.environ.get('MUNIN_STATEFILE', mode + '-STATEFILE')
    try:
        with open(wifi_filename) as f:
            stations = json.load(f)
    except FileNotFoundError:
        stations = dict()

    current_time = time.time()
    # refresh current stations
    for station in data:
        hostname = station['hostname']
        stations[hostname] = current_time

    # remove old stations (not seen since one year)
    to_remove = list()
    for station in stations:
        if current_time - stations[station] > 365 * 24 * 60 * 60:
            to_remove.append(station)
    for station in to_remove:
        del stations[station]

    # update JSON file
    with open(wifi_filename, "w") as f:
        json.dump(stations, f)

    return stations

def query_wifi_stations():
    stations = get_wifi_stations()

    current_time = time.time()
    for station in stations:
        # seen in the lastest 5 minutes?
        if current_time - stations[station] < 5 * 60:
            value = 1
        else:
            value = 0
        station_safe = station.replace(" ", "_")
        print('{}.value {}'.format(station_safe, value))

def query_wifi_bytes():
    data = freebox.api('wifi/ap/0/stations/')

    fields = dict()
    for field in get_fields(mode):
        fields[field] = 0
    for station in data:
        for field in get_fields(mode):
            fields[field] += station[field]
    for field in get_fields(mode):
        print('{}.value {}'.format(field, fields[field]))


def query_connection():
    data = freebox.api('connection/')

    for field in get_fields(mode):
        print('{}.value {}'.format(field, data.get(field)))


def query_switch(interface, mode):
    data = freebox.api('switch/port/{}/stats'.format(interface))

    for field in get_fields(mode):
        print('{}.value {}'.format(field, data.get(field)))


def query_transmission_traffic_data():
    data = freebox.api('downloads/stats/')

    # When combining upload+download on the same graph, download should be negative
    print('tx_rate.value {}'.format(data.get(field_tx_rate)))
    print('tx_throttling.value {}'.format(data.get('throttling_rate').get('tx_rate')))
    print('rx_rate.value {}'.format(-1 * data.get(field_rx_rate)))
    print('rx_throttling.value {}'.format(-1 * data.get('throttling_rate').get('rx_rate')))


def get_switch_stations(interface_idx):
    data = freebox.api('switch/status/')

    # the filename is something like
    # /var/lib/munin-node/plugin-state/nobody/freebox-switch-stations*
    switch_filename = os.environ.get('MUNIN_STATEFILE', mode + '-STATEFILE')
    try:
        with open(switch_filename) as f:
            stations = json.load(f)
    except FileNotFoundError:
        stations = dict()

    current_time = time.time()
    # refresh current stations
    for interface in data:
        if interface['name'][-1] is not interface_idx:
            continue
        mac_list = interface.get('mac_list', [])
        for host in mac_list:
            key = host['hostname'].strip().replace('.', '_')
            stations[key] = {'last_seen': current_time,
                    'hostname': host['hostname']}

    # remove old stations (not seen since one year)
    to_remove = list()
    for station in stations:
        if current_time - stations[station]['last_seen'] > 365 * 24 * 60 * 60:
            to_remove.append(station)
    for station in to_remove:
        del stations[station]

    # update JSON file
    with open(switch_filename, "w") as f:
        json.dump(stations, f)

    return stations


def query_switch_stations(interface):
    stations = get_switch_stations(interface)

    current_time = time.time()
    for station in stations:
        # seen in the lastest 5 minutes?
        if current_time - stations[station]['last_seen'] < 5 * 60:
            value = 1
        else:
            value = 0
        station_safe = station.replace(" ", "_")
        print('{}.value {}'.format(station_safe, value))


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


freebox = Freebox()

# Freebox authorization
if args.arg == 'authorize':
    exit_code = freebox.api_authorize()
    sys.exit(exit_code)

# Mode, determined by symlink name
mode = args.mode

if mode not in modes and mode != 'all':
    print('Unknown mode {}'.format(mode))
    print('Accepted modes are {}'.format(', '.join(modes)))
    sys.exit(1)

try:
    freebox.retrieve()
except FreeboxNoState:
    print('Could not load Freebox from saved state.')
    sys.exit(1)

if args.arg == 'config':
    print_config()
    sys.exit(0)

# Great for testing
if mode == 'all':
    COLORS = {
            'blue': '\033[34m',
            'red': '\033[31m',
            'normal': '\033[0m',
             }
    for m in modes:
        mode = m
        print(COLORS['red'] + "Testing mode:", mode)
        print(COLORS['blue'] + "config:" + COLORS['normal'])
        print_config()
        print(COLORS['blue'] + "data:" + COLORS['normal'])
        query_data()

    sys.exit(0)

# Query data
query_data()
