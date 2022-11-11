'''
Init devices
'''

import interface.modules.init.init_glob_vars as g
from interface.flask_app import *
from interface.modules.misc_import import *
from threading import Thread

from modules.devices.Evolve512 import EVOLVE as EV
from modules.devices.Zyla import ZYLA as ZY
from modules.devices.Prior import PRIOR
from modules.devices.Olympuslx81 import OLYMP
from modules.devices.CoolLedPe4000 import COOLLED
from modules.devices.LdynamicsXCite import XCITE
from modules.devices.gates import GATES
from modules.devices.sensors import SENSORS

import socket


pr = PRIOR()                                    # position x,y
ol = OLYMP()                                    # microscope
co = COOLLED()                                  # fluo
xc = XCITE()                                    # light for DMD
ga = GATES()                                    # gates control
se = SENSORS()

def calib_temp(temp_val):
    '''
    '''
    temp = str(round(26+(temp_val - 2450)/50,1))
    return temp


def make_dic_sensors_infos(sensors_infos):
    '''
    '''
    sens_split = sensors_infos.strip().split(',')
    temp_val = float(sens_split[1].split(':')[1])
    temp = calib_temp(temp_val)
    dic_sensors_infos = { 'light': sens_split[0].split(':')[1],
                          'temp': temp }
    return dic_sensors_infos


def retrieve_sensors_infos(debug=[]):
    '''
    '''
    addr_info_sensors = opj('interface','static', 'sensors', 'sensors.yaml')
    addr_mda_info_sensors = opj('mda_temp', 'monitorings', 'sensors.yaml')
    meas_interv = 5
    while 1:
        sleep(meas_interv)
        try:
            sensors_infos = se.read()
        except:
            sensors_infos = 'light: null, temp: null'
        if 0 in debug:
            print(f'Sensors infos : {sensors_infos}')
        try:
            dic_sensors_infos = make_dic_sensors_infos(sensors_infos)
        except:
            if 2 in debug:
                print('Cannot make the dictionary for sensors.. ')
            dic_sensors_infos = {'light':'0', 'temp':'0'}
        if 1 in debug:
            print(f'dic_sensor_infos : {dic_sensors_infos}')

        with open(addr_info_sensors, "w") as f_w:
            yaml.dump(dic_sensors_infos, f_w)
        if g.mda_launched:
            if 3 in debug:
                print('save sensors info for mda..')
            meas_interv = 10
            # mda_time_start
            if ope(addr_info_sensors):
                with open(addr_info_sensors, "r") as f_r0:
                    dic_sens = yaml.load(f_r0, Loader=yaml.FullLoader)
                    if ope(addr_mda_info_sensors):
                        with open(addr_mda_info_sensors, "r") as f_r1:
                            dic_sens_mda = yaml.load(f_r1, Loader=yaml.FullLoader)
                            tmeas = str(round( time()-g.mda_time_start ))
                            dic_sens_mda[tmeas] = dic_sens
                            if 4 in debug:
                                print(f'dic_sens_mda is { dic_sens_mda }')
                        with open(addr_mda_info_sensors, "w") as f_w:
                            yaml.dump(dic_sens_mda, f_w)
                    else:
                        print(f'Cannot find {addr_mda_info_sensors}')
            else:
                print(f'Cannot find {addr_info_sensors}')

thread_sensors = Thread(target=retrieve_sensors_infos)
thread_sensors.start()


def test_xcite(xc):
    '''
    Check few operations
    '''
    delay = 0.5
    sleep(delay)
    xc.shut_on()
    sleep(delay)
    xc.set_intens_level(1)
    sleep(delay)
    xc.set_intens_level(12)
    sleep(delay)
    xc.set_intens_level(0)
    sleep(delay)
    xc.shut_off()
    sleep(delay)
    xc.shut_on()
    sleep(delay)
    xc.shut_off()
