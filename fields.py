from modes import *

# mode_traffic
field_rate_down = 'rate_down'
field_bw_down = 'bw_down'
field_rate_up = 'rate_up'
field_bw_up = 'bw_up'

# mode_temp
field_cpum = 'cpum'
field_cpub = 'cpub'
field_sw = 'sw'
field_hdd = 'hdd'

# mode_xdsl
field_snr_down = 'snr_down'
field_snr_up = 'snr_up'

# mode_xdsl_errors
field_fec = 'fec'
field_crc = 'crc'
field_hec = 'hec'
field_es = 'es'
field_ses = 'ses'

# mode_switch1
field_rx1 = 'rx_1'
field_tx1 = 'tx_1'
# mode_switch2
field_rx2 = 'rx_2'
field_tx2 = 'tx_2'
# mode_switch3
field_rx3 = 'rx_3'
field_tx3 = 'tx_3'
# mode_switch4
field_rx4 = 'rx_4'
field_tx4 = 'tx_4'

fields = {
    mode_traffic: [
        field_rate_down,
        field_bw_down,
        field_rate_up,
        field_bw_up
    ],
    mode_temp: [
        field_cpum,
        field_cpub,
        field_sw,
        field_hdd
    ],
    mode_xdsl: [
        field_snr_down,
        field_snr_up
    ],
    mode_xdsl_errors: [
        field_fec,
        field_crc,
        field_hec,
        field_es,
        field_ses
    ],
    mode_switch1: [
        field_rx1,
        field_tx1
    ],
    mode_switch2: [
        field_rx2,
        field_tx2
    ],
    mode_switch3: [
        field_rx3,
        field_tx3
    ],
    mode_switch4: [
        field_rx4,
        field_tx4
    ]
}

xdsl_errors_fields_descriptions = {
    field_fec: 'FEC (Forward Error Connection)',
    field_crc: 'CRC (Cyclic Redundancy Check)',
    field_hec: 'HEC (Header Error Control)',
    field_es: 'ES (Errored Seconds)',
    field_ses: 'SES (Severely Errored Seconds)'
}


def get_fields(mode):
    if mode not in modes:
        print('Unknown mode {}'.format(mode))

    return fields[mode]
