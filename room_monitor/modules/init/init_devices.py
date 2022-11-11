from threading import Thread
from room_monitor.modules.misc_import import *
from room_monitor.modules.devices.sensors import SENSORS
from bokeh.plotting import figure, output_file, save
from time import time

import socket

se = SENSORS()

addr_info_sensors = opj('room_monitor','static', 'monitorings', 'sensors.yaml')
dic_sensors = {}

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


def retrieve_sensors_infos(debug=[0]):
    '''
    Regularly read the infos from sensors..
    '''
    t0 = time()
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
        curr_time = round(time()-t0,1)
        dic_sensors[curr_time] = dic_sensors_infos

        make_light_fig()
        make_temp_fig()

        with open(addr_info_sensors, "w") as f_w:
            yaml.dump(dic_sensors_infos, f_w)


def make_sensor_html_fig(target, debug=[0,1]):
    '''
    Html interactive figure for the sensor
    '''
    print('sensors items.. ')
    # try:
    if 0 in debug:
        print(f'target is {target}')
        print(f'dic_sensors is {dic_sensors}')
    xtarg, ytarg = [],[]

    for k,v in dic_sensors.items():
        if 1 in debug:
            print(f'v is {v}')
        if v[target].strip() != 'null':
            xtarg.append(int(k))
            ytarg.append(float(v[target]))
    p = figure(title=f"{target} curve", plot_width=300, plot_height=200)
    p.line(xtarg, ytarg)
    p.toolbar.logo = None

    addr_fig_targ = f"room_monitor/static/monitorings/{target}_curve.html"
    print(f'address curve light is {addr_fig_targ}')
    output_file(addr_fig_targ)
    save(p)
    print(f'Saved the figure at the address {addr_fig_targ}')
    # except:
    #     print(f'Cannot plot the {target} monitoring..')


def make_light_fig():
    '''
    Figure for the light monitoring..
    '''
    make_sensor_html_fig('light')


def make_temp_fig():
    '''
    Figure for the temp monitoring..
    '''
    make_sensor_html_fig('temp')


thread_sensors = Thread(target=retrieve_sensors_infos)
thread_sensors.start()
