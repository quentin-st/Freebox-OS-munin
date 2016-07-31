#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import argparse
import sys


# Useful for development
force_config = True
force_mode = True
forced_mode = 'freebox-traffic'

# Mode: either '', ... determined by symlink name
mode = __file__.split('/')[-1]
if force_mode:
    mode = forced_mode

modes = [
    'freebox-traffic',
    'freebox-temp',
    'freebox-xdsl',
    'freebox-switch1'
    'freebox-switch2'
    'freebox-switch3'
    'freebox-switch4'
]

if mode not in modes:
    print('Unknown mode {}'.format(mode))
    print('Accepted modes are {}'.format(', '.join(modes)))
    sys.exit(1)

# Munin config mode
parser = argparse.ArgumentParser()
parser.add_argument('config', nargs='?')
args = parser.parse_args()

if args.config == 'config' or force_config:
    if mode == 'freebox-traffic':
        print('graph_title Freebox traffic')
        print('graph_vlabel bits in (-) / out (+) per second')
        print('up.label Up (B/s)')
        print('up.draw AREA')
        print('down.label Down (B/s)')
        print('down.draw AREA')
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
