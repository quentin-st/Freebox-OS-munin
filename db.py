from munin.fields import *

db_net = 'net'
db_temp = 'temp'
db_dsl = 'dsl'
db_switch = 'switch'

dbs = {
    field_rate_down: db_net,
    field_bw_down: db_net,
    field_rate_up: db_net,
    field_bw_up: db_net,
    
    field_cpum: db_temp,
    field_cpub: db_temp,
    field_sw: db_temp,
    field_hdd: db_temp,

    field_fan_speed: db_temp,
    
    field_snr_down: db_dsl,
    field_snr_up: db_dsl,
    
    field_rx1: db_switch,
    field_tx1: db_switch,
    field_rx2: db_switch,
    field_tx2: db_switch,
    field_rx3: db_switch,
    field_tx3: db_switch,
    field_rx4: db_switch,
    field_tx4: db_switch
}


def get_db(field):
    return dbs[field]
