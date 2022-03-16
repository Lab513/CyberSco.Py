#!/usr/bin/env python
# encoding: utf-8

"""

CyberScoPy

python -m interface.run

"""
from __future__ import print_function, division, absolute_import

import requests as req
import oyaml as yaml
import json
# Flask imports
from flask import Flask, render_template, request, redirect, url_for
# flask_socketio version 5.0.1
from flask_socketio import SocketIO, emit
from PIL import Image
from io import BytesIO
from interface.modules.pages.define_all_pages import *

from modules.devices.Evolve512 import EVOLVE as EV
from modules.devices.Zyla import ZYLA as ZY
from modules.devices.Prior import PRIOR
from modules.devices.Olympuslx81 import OLYMP
from modules.devices.CoolLedPe4000 import COOLLED
from modules.devices.LdynamicsXCite import XCITE
from modules.devices.gates import GATES
from modules.mda import MDA

from interface.modules.util_interf import find_platform, launch_browser, init
from interface.modules.sweep import SWEEP
from modules.modules_mda.take_pic_fluo_or_BF import TAKE_PIC_FLUO_OR_BF as TPFB
from modules.util_misc import *
from time import sleep
from pathlib import Path
from datetime import datetime
from colorama import Fore, Style         # Color in the Terminal
import importlib
import socket
import base64
import os
platf = find_platform()

# from hanging_threads import start_monitoring
# start_monitoring(seconds_frozen=10, test_interval=100)

if platf == 'win':
    import gevent as server
    from gevent import monkey
    monkey.patch_all()
    print('Using gevent')
else:
    import eventlet as server
    server.monkey_patch()
    print('Using eventlet')

import glob

op = os.path
opd, opb, opj = op.dirname, op.basename, op.join

Debug = True            # Debug Flask

app = Flask(__name__)
app.config['UPLOADED_PATH'] = opj(os.getcwd(), 'interface', 'upload')
app.config['PIC_PATH'] = opj(os.getcwd(), 'interface',
                             'static', 'curr_pic', 'frame0.png')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'F34TF$($e34D'
socketio = SocketIO(app)


def date():
    '''
    Return a string with day, month, year, hour, minute and seconds
    '''
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")  # -%H-%M
    return dt_string

# Parameters

# displacement in x,y steps
prior_step = 100.0
# displacement in z with small steps
z_small_step = 200
# displacement in z with big steps
z_big_step = 10000
dic_mv = {'right': [-1, 0], 'left': [1, 0],
          'up': [0, -1], 'down': [0, 1]}
dic_mvz = {'up': 'N', 'down': 'F'}
list_pos = []              # list of the positions given to the mda
dic_pos_gate = {}          # dictionary pos <--> gate
modif_pos = 0
reload_pos = []
currview = 'simple'
dic_displ_obj = {'20x': 0.780, '40x': 0.390, '60x': 0.260, '100x': 0.156}
predefined_mda = True
monitor_params = {'mail': False, 'teams': False, 'delay_messages': 20}
kind_focus = 'afml_sweep'    # kind of autofocus used
afml_optim = 'max'     # 'steep_max_left' # 'steep_right' # 'max'

pr = PRIOR()                                    # position x,y
ol = OLYMP()                                    # microscope
co = COOLLED()                                  # fluo
xc = XCITE()                                    # light for DMD
ga = GATES()                                    # gates control

settings_folder = Path('interface') / 'settings'
# sweeping tool
swp = SWEEP(pr, ol, dic_displ_obj, emit, server)
# take picture fluo or bf for SNAP
tpfb = TPFB(ol, co, emit)

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

def init_system(debug=[0,1]):
    '''
    Initialize the devices
    '''
    if 0 in debug:
        print('Initialise the devices !!!')
    ol.pr = pr
    ol.set_wheel_filter(1)       # set wheel filter for BF
    sleep(1)
    ol.set_shutter(shut='on')    # open the shutter for BF
    ol.set_intens(2)             # init microscope light intensity
    try:
        print('Init Xcite')
        xc.init_XCite()
        test_xcite(xc)
        if 1 in debug:
            print('XCite init done')
    except:
        print('Cannot initialize XCite')
    try:
        ga.init_gate(100000)      # init all the LEDs off
    except:
        print('Cannot init gate..')

# try:
init_system()
# except:
#     print('Cannot initialize..')


def devices_connected(debug=[]):
    '''
    Send the informations concerning the devices connexion..
    '''
    if 0 in debug:
        print('### devices_connected ')
    for device in [pr, ol, co, xc, ga]:
        state = f'{device.name}:{device.state}'
        if 0 in debug:
            print(f'state to be sent is  {state} ')
        sleep(0.1)
        emit('connexion_state', state, broadcast=True)


def infos_hard_soft(debug=[]):
    '''
    Send to the client informations about computing ressource..
    '''
    try:
        hard_soft_infos = get_computing_infos()
        if 0 in debug:
            print(f'hard_soft_infos are {hard_soft_infos}')
        emit('hard_soft_infos', {'mess': json.dumps(hard_soft_infos)})
    except:
        print('probably working out of context')


@socketio.on('connect')
def test_connect():
    '''
    Websocket connections
    Sending informations to the client
    '''
    emit('response', {'data': 'Connected'})
    sending_ip()                # ip for live cam
    sending_posz()              # position in z for the interface
    sending_steps()             # send the values of the steps
    # send the values for the setting channels by default
    sending_set_chan('BF')
    sending_saved_set_chan()    # send the saved setting channels
    sending_masks()             # send the masks
    sending_objective()         # send the current objective used
    sending_predef()
    sending_all_models()        # send the aliases of all the models in use
    sending_event_model()       # send the event model
    # sending initial position information to the client
    double_sending_pos()
    devices_connected()         # connected devices
    infos_hard_soft()           # infos about GPU and ML framework

# Initialization of the Interface


@app.route('/')
def index():
    '''
    Introduction page
    '''
    dfp = define_firstpage()
    return render_template('intro_page.html', **dfp.__dict__)


@app.route('/interf', methods=['GET', 'POST'])
def interf(debug=[]):
    '''
    Interface page
    '''
    dip = define_index_page()
    if 0 in debug:
        print(f'dip is {dip.__dict__}')
    return render_template('index_folder.html', **dip.__dict__)


def make_protocol_list(debug=[]):
    '''
    List of the protocols
    '''
    addr_prot = 'interface/static/mda_protocols/*.yaml'
    # list of the yaml protocols
    protocols_list = [opb(f).split('.yaml')[0] for f in glob.glob(addr_prot)]
    protocols_list.remove('temp0')
    if 1 in debug:
        print(f'protocols_list {protocols_list}')

    return protocols_list


@socketio.on('save_protocol')
def save_protocol(dicp):
    '''
    Save  the protocol as a yaml file
    '''
    # new created protocol
    dic_prot = json.loads(dicp)
    addr_prot_saved = opj('interface', 'static',
                          'mda_protocols', dic_prot['newname'])
    prot_saved = opb(addr_prot_saved).split('.yaml')[0]
    if prot_saved[0].isalpha() or prot_saved == '@predef_prot':
        print(f'### addr_prot_saved {addr_prot_saved} ')
        with open(addr_prot_saved, 'w') as f_w:
            yaml.dump(dic_prot['tree'],
                      f_w,
                      allow_unicode=True,
                      default_flow_style=False)
    else:
        print('First letter must be alphabetical..')
    # recreate list of protocols
    protocols_list = make_protocol_list()
    # refresh the list in the select list
    emit('refresh_list_protocols', json.dumps(protocols_list))

    return redirect(url_for('index'))


@socketio.on('delete_protocol')
def delete_protocol(dicp):
    '''
    Delete the current protocol
    '''
    dic_prot = json.loads(dicp)
    file_to_remove = opj('interface', 'static',
                         'mda_protocols', dic_prot['nameprotoc'])
    print(f'### file_to_remove {file_to_remove} ')
    if '@predef_prot' not in file_to_remove:      # protecting @predef_prot
        os.remove(file_to_remove)
    protocols_list = make_protocol_list()
    # refresh the list in the select list
    emit('refresh_list_protocols', json.dumps(protocols_list))

    return redirect(url_for('index'))


@socketio.on('read_yaml')
def read_yaml(name_yaml, debug=[1]):
    '''
    Read_yaml and send the json for loading the protocol in the tree
    '''
    addr_yaml = opj('interface', 'static', 'mda_protocols', name_yaml)
    if 1 in debug:
        print(f'addr_yaml {addr_yaml}')
    try:
        with open(addr_yaml) as f_r:
            yaml_file = yaml.load(f_r, Loader=yaml.FullLoader)
            # transmit with json
            emit('prot_json', json.dumps(yaml_file))
    except:
        print('Cannot read the yaml file')
    # corrections in the tree for predef
    if name_yaml == 'temp0.yaml':
        emit('correct_tree', '')


@socketio.on('launch_tree_protocol')
def launch_tree_protocol(curr_prot):
    '''
    Protocol from the tree
    '''
    global yaml_prot
    yaml_prot = curr_prot + '.yaml'
    print(Fore.GREEN + f"Launch the protocol"
                       f" {curr_prot} from the tree panel !!!!")
    print(Style.RESET_ALL)


@socketio.on('new_pic')
def new_pic(msg):
    '''
    Changing the camera image
    '''
    print('take new pic')
    # take a new pic
    ev.take_pic(app.config['PIC_PATH'])


def double_sending_pos():
    '''
    '''
    sending_pos()
    sending_pos()


def retrievexy(debug=[]):
    '''
    Retrieve positions x and y
    '''
    posx = pr.ask_pos('x')
    posy = pr.ask_pos('y')
    if 0 in debug:
        print(f'posx is {posx}; posy is {posy}')
    return posx, posy


def sending_ip():
    '''
    Send the Ip for the camera
    '''
    global ip
    ip = socket.gethostbyname(socket.gethostname())
    emit('ip_used', ip, broadcast=True)


def sending_pos(debug=[]):
    '''
    Send the position to the interface
    '''
    if 0 in debug:
        print('sending the position x and y to the interface')
    posx, posy = retrievexy()
    while posx == posy:                    # avoid x = y
        posx, posy = retrievexy()
    emit('new_posx', f'{posx}', broadcast=True)
    emit('new_posy', f'{posy}', broadcast=True)


def sending_posz(debug=[]):
    '''
    Send the position in axis z to the interface
    '''
    if 0 in debug:
        print('sending the position z to the interface')
    # ask for current pos z
    posz = ol.ask_zpos()
    print(f'current posz is {posz}')
    # pos z sent to the interface in µm
    posz_sent = round(posz/100, 1)
    emit('posz', f'{posz_sent}', broadcast=True)      # emit pos z


def sending_steps(debug=[]):
    '''
    Send the steps for x, y and z displacements to the interface
    '''
    if 0 in debug:
        print('sending the steps values to the interface')
    str_steps = json.dumps({"stepxy": prior_step, "stepz": z_small_step})
    emit('steps_xyz', f'{str_steps}', broadcast=True)


@socketio.on('load_new_SC')
def change_set_chan(new_SC):
    '''
    '''
    print(f'new_SC is {new_SC}')
    sending_set_chan(new_SC)


def sending_set_chan(SC, debug=[]):
    '''
    Send the values of the setting channels from yaml to interface
    '''
    global dic_chan_set
    if 0 in debug:
        print('sending settings channel to the interface')
    addr_SC = settings_folder / 'settings_channels' / f'{SC}.yaml'
    if 0 in debug:
        print(f'addr_SC is {addr_SC}')
    with open(addr_SC) as f_r:
        dic_chan_set = yaml.load(f_r, Loader=yaml.FullLoader)
    if 0 in debug:
        print(f'In sending_set_chan, dic_chan_set is {dic_chan_set}')
    str_set_chan = json.dumps(dic_chan_set)
    emit('set_chan', f'{str_set_chan}', broadcast=True)


def sending_saved_set_chan(curr_SC='BF', debug=[]):
    '''
    Send the saved setting channels
    '''
    if 0 in debug:
        print('sending saved settings channel to the interface')
    list_yaml = os.listdir(settings_folder / 'settings_channels')
    list_SC = [sc.split('.yaml')[0] for sc in list_yaml]
    if 0 in debug:
        print(f'list_SC is {list_SC}')
    dic_SC = {'curr_SC': curr_SC, 'list_SC': list_SC}
    str_saved_set_chan = json.dumps(dic_SC)
    emit('saved_set_chan', f'{str_saved_set_chan}', broadcast=True)


def sending_masks(debug=[]):
    '''
    Send the masks names
    '''
    if 0 in debug:
        print('sending the masks')
    dmd_path = Path('interface') / 'static' / 'dmd'
    list_png = [opb(str(add)) for add in list(dmd_path.glob('*.png'))]
    list_dmd_pics = [im_png[:-4] for im_png in list_png]
    if 1 in debug:
        print(f'list_dmd_pics is {list_dmd_pics}')
    str_list_dmd_pics = json.dumps(list_dmd_pics)
    emit('dmd_masks', f'{str_list_dmd_pics}', broadcast=True)


def sending_objective(debug=[]):
    '''
    Send to the interface, the current objective value
    '''
    curr_obj = ol.ask_objective()
    emit('curr_objective', curr_obj, broadcast=True)
    if 1 in debug:
        print(f'sent the current objective {curr_obj} to the interface..')


def find_exp_name(add_name, debug=[]):
    '''
    Extract the name of the predefined
    experiment from the predefined python experiment file..
    '''
    if 0 in debug:
        print(add_name)
    expr = 'name :'
    with open(add_name) as f_r:
        ll = f_r.readlines()
        name_exp = None
        for l in ll:
            if expr in l:
                name_exp = l.split(expr)[1].strip()
    return name_exp


def find_exp_descr(add_descr, debug=[]):
    '''
    Retrieve the description for the tooltip
    from the python predefined experiment file
    '''
    if 0 in debug:
        print(add_descr)
    expr = 'description :'
    with open(add_descr) as f_r:
        ll = f_r.readlines()
        descr = ""
        take_line = False
        for l in ll:
            if expr in l:
                descr = l.split(expr)[1]
                take_line = True
            elif take_line and not ((expr in l) or ("'''" in l)):
                descr += l
            if "'''" in l:
                take_line = False
                if descr:
                    break
    if 0 in debug:
        print(f'descr {descr}')
    return descr


def sending_predef(debug=[]):
    '''
    Preset experiments
    '''
    addr_plugins = opj('modules', 'predef', 'plugins')
    # list addresses plugins
    lplugs = glob.glob(f'{addr_plugins}/*.py')
    list_plugins = [p for p in lplugs if '__init__' not in p]
    # association name_exp to name plugin, description etc..
    dic_exp = {}
    for addr in list_plugins:
        # retrieving the preset experiment name
        name_exp = find_exp_name(addr)
        descr_exp = find_exp_descr(addr)
        if name_exp:
            # if name exists add to dictionary
            dic_exp[name_exp] = {'name_plugin': opb(addr)[:-10],
                                 'descr_plugin': descr_exp}
    dic_plugins = json.dumps(dic_exp)
    emit('predef_mdas', dic_plugins, broadcast=True)
    if 1 in debug:
        print(f'sending the plugins')
        print(f'dic_plugins = {dic_plugins}')


@socketio.on('change_obj')
def change_objective(obj):
    '''
    Select a new objective
    '''
    ol.select_obj(obj)
    print(f'Changed objective to {obj}')


@socketio.on('change_AF')
def change_AF(af):
    '''
    Choose the aufocus method
    '''
    # kind of autofocus used.. set from interface
    global kind_focus
    print(f'Using the AF method {af}')
    kind_focus = af


def sending_curr_model(debug=[]):
    '''
    Send to the interface which main segmentation model is used
    '''
    with open('modules/settings/curr_model.yaml') as f_r:
        curr_model = yaml.load(f_r, Loader=yaml.FullLoader)
    emit('curr_model', curr_model, broadcast=True)
    if 0 in debug:
        print(f'sent the current model name : {curr_model} to the interface..')


def sending_all_models(debug=[]):
    '''
    Send to the interface all the models..
    '''
    with open('modules/settings/models.yaml') as f_r:
        all_models = yaml.load(f_r, Loader=yaml.FullLoader)
    if 0 in debug:
        print(f'all_models.keys() is {all_models.keys()}')
    # list of the models aliases
    list_models = json.dumps(list(all_models.keys()))
    emit('all_models', list_models, broadcast=True)
    if 0 in debug:
        print(f'sent all_models.keys()'
              f' : {all_models.keys()} to the interface..')
    sleep(1)
    sending_curr_model()


def sending_event_model(debug=[]):
    '''
    Send to the interface the event model
    '''
    with open('modules/settings/event_model.yaml') as f_r:
        ev_mod = yaml.load(f_r, Loader=yaml.FullLoader)
    emit('used_event_model', ev_mod, broadcast=True)
    if 0 in debug:
        print(f'sent the event model name : {ev_mod} to the interface..')


@socketio.on('change_model')
def change_model(model):
    '''
    '''
    with open('modules/settings/curr_model.yaml', 'w') as f_w:
        yaml.dump(model, f_w)         #
    print(f'Changed model to {model}')
    # emit('curr_model', model, broadcast=True)
    emit('new_model', model, broadcast=True)


def move_in_direct(direct):
    '''
    Move in the direction "direct" with step prior_step
    '''
    x = dic_mv[direct][0]*prior_step   # x relative move
    y = dic_mv[direct][1]*prior_step   # y relative move
    pr.relative_move_to(x, y)


def try_move_in_direct(direct):
    '''
    '''
    try:
        move_in_direct(direct)
    except:
        print('cannot send the move')


def movez_in_direct(direct, debug=[]):
    '''
    Move in the z direction ..
    '''
    if 1 in debug:
        print(f'z_small_step is {z_small_step}')
        print(f'dic_mvz[direct] is {dic_mvz[direct]}')
    # make a step in the z direction
    ol.set_zpos(z_small_step, move_type=dic_mvz[direct])


@socketio.on('move')
def move(direct, debug=[]):
    '''
    Move right, left up, down with command from interface
    '''
    if 1 in debug:
        print(f'message is {direct}')
    try_move_in_direct(direct)     # move the prior
    sending_pos()                  # send position to interface


@socketio.on('movez')
def movez(direct, debug=[]):
    '''
    Move on z axis up down with command from interface
    '''
    if 1 in debug:
        print(f'message is {direct}')
    movez_in_direct(direct)           # move in z
    sending_posz()                    # send position to interface


@socketio.on('offset')
def calc_offset(msg):
    '''
    Find the offset
    '''
    ol.calc_offset()      # calculation of the offset
    save_offset_and_posz()  # save the offset and pos z after autofocus in yaml
    sending_posz()           # position after autofocus
    emit('offset', ol.offset, broadcast=True)


@socketio.on('reset_offset')
def reset_offset(msg):
    '''
    recalculate the offset
    '''
    posz = ol.ask_zpos()
    ol.offset = posz - ol.af_pos     # Adapting the offset position
    print(Fore.YELLOW + f'offset is {ol.offset}')
    print(Style.RESET_ALL)
    emit('offset', ol.offset, broadcast=True)


#  refocusing
@socketio.on('refocus')
def refocus(msg):
    '''
    Refocus using the offset
    '''
    ol.refocus()            # go back to focused position
    sending_posz()          # send pos z to the interface


def save_offset_and_posz():
    '''
    Save the offset, the z after autofocus and z at focus
    '''
    zpos = ol.ask_zpos()
    print(f'zpos : {zpos} type(zpos) {type(zpos)}, '
          'ol.offset : {ol.offset} type(ol.offset) {type(ol.offset)} ')
    dic_z_offset = {'z': zpos,
                    'offset': ol.offset,
                    'zfocus': zpos + int(ol.offset),
                    'ref_posz': ol.ref_posz}
    print(f'** dic_z_offset is {dic_z_offset} ')
    with open('interface/settings/offset_and_posz.yaml', 'w') as f_w:
        # save the offset, the autofocus
        # position and the focused position in yaml
        yaml.dump(dic_z_offset, f_w)


#  refocusing
@socketio.on('access_back')
def access_back(msg):
    '''
    Give access back to the manual focus
    '''
    ol.give_access_back()             # go back to focused position


#  sweep the chip
@socketio.on('sweep_chip')
def sweep_chip(sweepings):
    '''
    sweep the chip
    '''
    swp.sweep_chip(sweepings)


#  sweep the chip
@socketio.on('coord_in_sweep')
def move_in_sweep(coords):
    '''
    After click in sweep area, go to the clicked position
    '''
    swp.move_in_sweep(coords)
    sleep(1)
    sending_pos()                           # send position to interface


def save_all_pos():
    '''
    Save the positions for the mda in settings folder
    '''
    addr_list_pos = settings_folder / 'list_pos.yaml'
    with open(addr_list_pos, 'w') as f_w:
        yaml.dump(list_pos, f_w)


# save the positions
@socketio.on('save_pos')
def save_pos(msg):
    '''
    Save, change, reload the positions
    '''
    global list_pos
    if not reload_pos:
        posx = pr.ask_pos('x')
        posy = pr.ask_pos('y')
        new_pos = [posx, posy]            # current position
    else:
        new_pos = reload_pos                # reload position
    if modif_pos:
        list_pos[curr_numpos] = new_pos         # change the existing position
        num_pos = curr_numpos
    else:
        list_pos += [new_pos]         # add a new position
        num_pos = len(list_pos)-1
    print(f'list_pos is {list_pos}')
    str_new_pos = json.dumps({"pos": new_pos, "numpos": num_pos})
    save_all_pos()
    emit('position_saved', str_new_pos)


#  save the associations pos <--> gate
@socketio.on('pos_gate')
def save_pos_gate(pgate):
    '''
    Saving gate associated to each position
    '''
    global dic_pos_gate
    dic_pgate = json.loads(pgate)
    for k, v in dic_pgate.items():
        dic_pos_gate[int(k)] = int(v)
    print(f'dic_pos_gate is {dic_pos_gate}')


@socketio.on('curr_numpos')                    #
def retrieve_curr_numpos(numpos):
    '''
    Retrieve the current position index
    '''
    global curr_numpos
    curr_numpos = int(numpos)
    print(f'num position is {curr_numpos}')


@socketio.on('modif_pos')                    #
def allow_modif_pos(modif):
    '''
    Allowing position modif
    '''
    global modif_pos
    modif_pos = int(modif)
    print(f'modif_pos is {modif_pos}')


def reload_offset(debug=[]):
    '''
    '''
    addr_offset_and_posz = settings_folder / 'offset_and_posz.yaml'
    # offset and z position
    with open(addr_offset_and_posz) as f_r:
        dic_zoff = yaml.load(f_r)
        ol.offset = dic_zoff['offset']         # offset
        ol.ref_posz = dic_zoff['ref_posz']     # reference position for refocus
        ol.set_lim_af_sup_and_inf()                  # set excursion limits
    if 1 in debug:
        print(f'dic_zoff is {dic_zoff}')


@socketio.on('reload_pos')
def reload_positions(pos_reload):
    '''
    Reloading the positions
    '''
    global reload_pos
    print(f'reloading the registered positions !!!')
    reload_offset()
    addr_list_pos = settings_folder / 'list_pos.yaml'
    with open(addr_list_pos) as f_r:        # list of the positions
        lpos = yaml.load(f_r)
    print(f'lpos is {lpos}')
    for pos in lpos:
        reload_pos = [pos[0], pos[1]]
        save_pos('')              # inlcude the pos in the current experiment
    reload_pos = []


#  move to x,y
@socketio.on('moveto')
def moveto(pos):
    '''
    Move to the position
    '''
    print(f'position is {pos}')
    newpos = json.loads(pos)
    x, y = newpos[0], newpos[1]        # x,y floats in µm
    pr.absolute_move_to(x, y)


@socketio.on('fast_z_pos')              # move fast on the z axis
def fast_z_pos(zpos):
    '''
    fast_z_pos
    '''
    ol.set_zpos(int(zpos), move_type='d')          # move to the pos z
    sleep(1)
    print(f'value received for fast_z_pos is  {zpos}')
    sending_posz()              # send the z position to the interface


@socketio.on('save_z_pos')            # move fast on the z axis
def save_z_pos(zpos):
    '''
    Save z position
    '''
    addr_posz = settings_folder / 'posz.yaml'
    with open(addr_posz, 'w') as f_w:
        yaml.dump(zpos, f_w)
    ol.ref_posz = zpos           # save ol.ref_posz for Autofocus
    # arbitrary value for offset for prog to work with AF_ML
    ol.offset = 10
    emit('saved_z', f'{zpos}', broadcast=True)


@socketio.on('return_z_pos')           # move fast on the z axis
def return_z_pos(msg):
    '''
    Set the pos z of the objective to the saved position in z
    '''
    addr_posz = settings_folder / 'posz.yaml'
    with open(addr_posz) as f_r:
        zpos = yaml.load(f_r, Loader=yaml.FullLoader)
        # move to the pos z
        ol.set_zpos(int(zpos), move_type='d')
        sleep(1)
        print(f'value received for return_z_pos is  {zpos}')
        # pos z sent to the interface in µm
        posz_sent = round(zpos/100, 1)
        emit('posz', f'{posz_sent}', broadcast=True)


@socketio.on('fast_xy_pos')                     # move fast to x,y
def fast_xy_pos(xypos):
    '''
    fast_xy_pos
    '''
    dic_pos_xy = json.loads(xypos)
    print(f'dic_pos_xy is {dic_pos_xy}')
    x, y = float(dic_pos_xy['x']), float(dic_pos_xy['y'])
    pr.absolute_move_to(x, y)
    sending_pos()


@socketio.on('set_stepxy')                          # step xy
def set_stepxy(stepxy):
    '''
    stepxy
    '''
    global prior_step
    dic_stepxy = json.loads(stepxy)
    print(f'dic_stepxy is {dic_stepxy}')
    prior_step = int(dic_stepxy['stepxy'])/100     # step xy in µm


@socketio.on('set_stepz')                          # step z
def set_stepz(stepz):
    '''
    stepz
    '''
    global z_small_step
    dic_stepz = json.loads(stepz)
    print(f'dic_stepz is {dic_stepz}')
    z_small_step = int(dic_stepz['stepz'])


@socketio.on('update_position')
def update_pos(node_id, debug=[]):
    '''
    update the pos with id : node_id
    '''
    print(f'######### Updating the position from the tree !!!!')
    posx, posy, posz = pr.ask_pos('x'), pr.ask_pos('y'), ol.ask_zpos()
    if 1 in debug:
        print(f'node_id is {node_id} ')
    if 2 in debug:
        print(f'posx is {posx}, posy is {posy}, posz is {posz} ')
    # refresh the infos in the tree
    idxyz = f'{node_id};{posx};{posy};{posz}'
    emit('update_xyz_infos', idxyz)


@socketio.on('update_af')
def update_af(node_id, debug=[]):
    '''
    update the pos with id : node_id
    '''
    print(f'######### Updating the offset for the ZDC AF from the tree !!!!')
    if 1 in debug:
        print(f'node_id is {node_id} ')
    posz = ol.ask_zpos()
    ol.calc_offset()
    ol.set_zpos(posz)
    print(f'Offset for id {node_id} is {ol.offset} ')
    # refresh the infos in the tree
    emit('update_af_infos', node_id + ';' + str(ol.offset))


@socketio.on('goto_position')
def go_pos(posxyz, debug=[]):
    '''
    go to the pos posxyz from the tree
    '''
    if 0 in debug:
        print(f'######### Go to the position {posxyz}')
    dic_posxyz = json.loads(posxyz)
    try:
        # refresh MDA picture
        with open(opj('mda_temp', 'mda_init', 'lpos_id.yaml')) as f_r:
            # list of the positions id
            lid = yaml.load(f_r, Loader=yaml.FullLoader)
        # current position (pos selected in the tree)
        curr_pos = lid.index(dic_posxyz['id'])
        print(f'curr_pos obtained from Id is {curr_pos} ')
        # change the current observed positon in the interface
        emit('watch_currpos', curr_pos)
    except:                                        # goto x,y,z
        print('no lpos_id.yaml file yet')
        # move in xy
        pr.absolute_move_to(float(dic_posxyz['x']), float(dic_posxyz['y']))
        if 3 in debug:
            print(f"dic_posxyz['z'] = {dic_posxyz['z']} ")
        # move in z
        ol.set_zpos(dic_posxyz['z'])
        sending_pos()


@socketio.on('save_chan_dict')          # set_chan_dict
def save_chan(dic_chan, debug=[1]):
    '''
    Save the Settings channels dictionary in settings/settings_channels folder
    and refresh the list in the interface
    '''
    global dic_chan_set
    dic_chan_set = json.loads(dic_chan)     # loading from interface
    if 1 in debug:
        print(f'dic_chan_set is {dic_chan_set}')
    folder_SC = settings_folder / 'settings_channels'
    if not os.path.exists(folder_SC):
        os.mkdir(folder_SC)
    name_SC = dic_chan_set['name_set_chan']
    with open(folder_SC / f'{name_SC}.yaml', 'w') as f_w:
        # save set channels to the yaml file
        addr = yaml.dump(dic_chan_set, f_w)
    sending_saved_set_chan(curr_SC=name_SC)    # refresh the list of SC
    if name_SC == 'BF':
        # intensity retrieved from BF setting channel
        intens = int(dic_chan_set['BF'])
        ol.set_intens(intens)                 # change the µscope BF intensity


@socketio.on('snap')
def snap(snap_val):
    '''
    Snap, Take an image online
    '''
    tpfb.take_pic(snap_val)         # retrieve snap exposure time


@socketio.on('snap_exp_time')
def snap_exp_time(snap_time, debug=[]):
    '''
    Snap exposure time
    '''
    if 0 in debug:
        print(f'snap_time is {snap_time}')
    emit('send_exp_time', snap_time)


@socketio.on('live_fluo_on')
def live_fluo_on(snap_val, debug=[0]):
    '''
    Set live fluo on
    '''
    if 0 in debug:
        print('illuminating continuously..')
    tpfb.illuminate(snap_val)


@socketio.on('live_fluo_off')
def live_fluo_off(msg):
    '''
    Set live fluo off
    '''
    tpfb.return_to_BF()


@socketio.on('ask_nb_cells')
def ask_emit_nb_cells(msg):
    '''
    Send to the interface the nb of cells from yaml
    '''
    try:
        with open('interface/static/mda_pics/nb_cells.yaml') as f_r:
            nb_cells = yaml.load(f_r, Loader=yaml.FullLoader)
            emit('real_time_nb_cells', nb_cells)
    except:
        print('Probably cannot find the file : nb_cells.yaml')


@socketio.on('name_img_mosaic')
def name_img_DMD(name_img_mosaic):
    '''
    Name for DMD image
    '''
    global name_img_dmd
    name_img_dmd = name_img_mosaic


@socketio.on('image_canvas')
def save_png_for_DMD(b64):
    '''
    Save the base64 image as png image for DMD
    '''
    b64 = b64.split('base64,')[1]
    im = Image.open(BytesIO(base64.b64decode(b64)))
    im.save(opj('interface', 'static', 'dmd',
                f'{name_img_dmd}.png'), 'PNG')
    sending_masks()                    # refresh masks list


@socketio.on('select_mda')             # select which mda to perform
def select_mda(sel_mda):
    '''
    '''
    print(f'selected mda is {sel_mda}')


@socketio.on('launch_mda')
def launch_mda(msg):             # launch the mda
    '''
    Close cam before launching the MDA
    '''
    print('close the cam')
    emit('close_cam', '')          # close cam to access it for the protocol
    emit('modif_interf', '')       # modify the interface


@socketio.on('choice_mda_scenario')
def choice_mda_scenario(msg):
    '''
    Retrieve the MDA scenario from the interface
    '''
    global curr_mda_scenario
    msgsplit = msg.split('select')
    print(f'msgsplit is {msgsplit} ')
    if msgsplit[0] != 'de':
        curr_mda_scenario = msgsplit[1].strip()
    else:
        curr_mda_scenario = None
    print(Fore.YELLOW + '************** ')
    print('')
    print(f'Selected scenario is {curr_mda_scenario} ')
    print('')
    print('************** ')
    print(Style.RESET_ALL)


def cam_choice():
    '''
    Choosing between Evolv, Zyla etc..
    '''
    with open(settings_folder / 'cam_used.yaml') as f_r:
        cam_used = yaml.load(f_r, Loader=yaml.FullLoader)
    if cam_used == 'Evolv':
        cam = EV()
    elif cam_used == 'Zyla':
        cam = ZY()

    return cam


def ask_experim_infos():
    '''
    Send message for retrieving the infos concerning the experiment
    '''
    emit('experim_infos')
    print('asked for experim infos..')


def ask_for_monitor_params():
    '''
    Send message for retrieving infos about how the experiment is monitored
    '''
    emit('monitor_settings')
    print('asked for monitor settings..')


@socketio.on('save_experim_infos')
def save_experim_infos(dic_infos):
    '''
    Save the infos about the MDA experiment
    '''
    experim_infos = json.loads(dic_infos)
    with open(Path('interface') / 'infos_mda' /
              'experiment_infos.yaml', 'w') as f_w:
        yaml.dump(experim_infos, f_w)
    print('experiment infos saved')


@socketio.on('monitor_params')
def monitor_params(dic_monitor_params, debug=[]):
    '''
    Parameters for monitoring the MDA
    '''
    global monitor_params
    monitor_params = json.loads(dic_monitor_params)
    if 0 in debug:
        print(f'monitor_params are {monitor_params} ')


def announcing_scenario():
    '''
    Message of introduction for the scenario
    '''
    print('##################')
    print(f'Applying scenario {curr_mda_scenario} ')
    print('##################')


@socketio.on('kind_mda')
def choice_predefined_or_free_mda(kind_mda, debug=[]):
    '''
    Predefined mda or free mda
    '''
    global predefined_mda
    if kind_mda == 'predefined_mda':     # choosing predefined mda
        predefined_mda = True
    else:
        predefined_mda = False           # choosing free mda
    if 0 in debug:
        print(f'predefined_mda is {predefined_mda} !!!')


def mda_params(mda):
    '''
    Retrieve parameters for the mda
    kind_focus : AF_ML, ZDC etc..
    afml_optim  : max, max_righ, max_left
    '''
    mda.kind_focus = kind_focus
    mda.afml_optim = afml_optim
    mda.monitor_params = monitor_params

    return mda


def launch_mda_tree(cam):
    '''
    Launch the protocol from the Tree tool
    '''
    # MDA protocol with attached devices
    mda_protocol = MDA(ldevices=[ol, pr, cam, co, xc, ga])
    mda_params(mda_protocol)
    ol.mod = mda_protocol.curr_mod
    ol.ref_posz = ol.ask_zpos()
    mda_protocol.load_tree_protocol(yaml_prot)    # Protocol from the tree
    save_list_id(mda_protocol)           # list id for goto
    mda_protocol.launch()               # launch the protocol


def save_list_id(mda_protocol):
    '''
    Save the list of the ids for predefined MDAs
    '''
    print(f'mda_protocol.lpos_id {mda_protocol.lpos_id} ')
    all_id = opj('mda_temp', 'mda_init', 'lpos_id.yaml')
    with open(all_id, "w") as f_w:
        yaml.dump(mda_protocol.lpos_id, f_w)


def save_list_pos(mda_protocol):
    '''
    Save the list of positions for predefined MDAs
    '''
    print(f'mda_protocol.lxyz {mda_protocol.lxyz} ')
    all_pos = opj('mda_temp', 'mda_init', 'lxyz.yaml')
    with open(all_pos, "w") as f_w:
        yaml.dump(mda_protocol.lxyz, f_w)


def save_list_offsets(mda_protocol):
    '''
    Save the list of the offsets
    '''
    print(f'mda_protocol.loffsets {mda_protocol.loffsets} ')
    all_pos = opj('mda_temp', 'mda_init', 'loffsets.yaml')
    with open(all_pos, "w") as f_w:
        yaml.dump(mda_protocol.loffsets, f_w)


def save_list_SC_ET(mda_protocol):
    '''
    Save the list of SC and ET for predefined MDAs
    '''
    print(f'mda_protocol.list_SC_ET {mda_protocol.list_SC_ET} ')
    all_SC_ET = opj('mda_temp', 'mda_init', 'list_SC_ET.yaml')
    with open(all_SC_ET, "w") as f_w:
        yaml.dump(mda_protocol.list_SC_ET, f_w)


def save_list_AF(mda_protocol, debug=[]):
    '''
    Save the list of AF for predefined MDAs
    The default autofocus is afml_sweep
    '''
    # by default afml_sweep
    mda_protocol.list_AF = ['afml_sweep' for af
                            in mda_protocol.list_AF if af is None]
    print(f'mda_protocol.list_AF {mda_protocol.list_AF} ')
    if 0 in debug:
        all_AF = opj('mda_temp', 'mda_init', 'list_AF.yaml')
    with open(all_AF, "w") as f_w:
        yaml.dump(mda_protocol.list_AF, f_w)


def save_list_gates(mda_protocol):
    '''
    Save the list of the gates for predefined MDAs
    '''
    print(f'mda_protocol.list_gates {mda_protocol.list_gates} ')
    all_gates = opj('mda_temp', 'mda_init', 'list_gates.yaml')
    with open(all_gates, "w") as f_w:
        yaml.dump(mda_protocol.list_gates, f_w)


def passing_from_tree_to_predefined(mda_protocol, debug=[]):
    '''
    Write in yaml files the informations from the tree
    to inject them after in the mda..
    '''
    mda_protocol.load_tree_protocol('@predef_prot.yaml')
    if 0 in debug:
        print(f'dir(mda_protocol) {dir(mda_protocol)} ')
    save_list_id(mda_protocol)
    save_list_pos(mda_protocol)
    save_list_offsets(mda_protocol)
    save_list_AF(mda_protocol)
    save_list_gates(mda_protocol)
    save_list_SC_ET(mda_protocol)


def launch_mda_predef(cam):
    '''
    Launch predefined experiment
    '''
    chosen_plugin = f'modules.predef.plugins.{curr_mda_scenario}_plugin'
    module = importlib.import_module(chosen_plugin)
    mda_protocol = getattr(module,
                           f'{curr_mda_scenario}'.upper())(
                            ldevices=[ol, pr, cam, co, xc, ga])
    # attaching the current segmentation model to the microscope for focus
    ol.mod = mda_protocol.curr_mod
    mda_params(mda_protocol)
    ##
    passing_from_tree_to_predefined(mda_protocol)
    ####
    mda_protocol.get_positions()        # retrieve the positions
    mda_protocol.get_gates()            # retrieve the gates association
    mda_protocol.get_chan_set()         # retrieve the channels settings
    mda_protocol.get_kind_focus()       # set positions focus kind..

    mda_protocol.define()


@socketio.on('make_mda')
def make_mda(msg):
    '''
    Launch the MDA
    '''
    sleep(10)                      # time for live cam to shut down properly
    ##
    ask_experim_infos()            # retrieve infos about the mda experiment
    # retrieve infos about how to monitor the experiment
    ask_for_monitor_params()
    ##
    sleep(2)
    ##
    cam = cam_choice()          # choosing beetween Evolv and Zyla
    ol.cam = cam                # attaching the camera to the µscope for focus
    ##
    if predefined_mda:
        launch_mda_predef(cam)
    else:
        launch_mda_tree(cam)


@socketio.on('curr_rep')
def current_step(rep):
    '''
    Index of the current iteration
    '''
    print(f'Curr step is {rep} !!!!')


@socketio.on('time_elapsed')
def time_lapsed(time_elapsed):
    '''
    Time elapsed since the beginning of the MDA
    '''
    print(f'time elapsed is {time_elapsed} !!!!')


@socketio.on('params')
def retrieve_params(prms):
    '''
    Retrieve the parameters from the interface
    '''
    global params
    params = json.loads(prms)


@app.route('/run-protocol', methods=['POST'])
def run_protocol():
    '''
    Retrieve the protocol from Node.js API
    '''
    protocol = request.json
    print(protocol)
    return 'OK'


def shutdown_server():
    '''
    Quit the application
    called by method shutdown() (hereunder)
    '''
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/shutdown')
def shutdown():
    '''
    Shutting down the server.
    '''
    shutdown_server()

    return 'Server shutting down...'


def message_at_beginning(host, port):
    '''
    '''
    print(Fore.YELLOW + """
    ***************************************************************
    CyberSco.py

    address: {0}:{1}

    """.format(host, port))


def set_IP():
    '''
    '''
    ip = socket.gethostbyname(socket.gethostname())
    dic_vid = {'host': ip, 'port': 2204}                # address for video
    with open(settings_folder / 'cam_address.yaml', 'w') as f_w:
        yaml.dump(dic_vid, f_w)         #
    # address for main interface # 5042
    dic_server = {'host': ip, 'port': 5042}
    with open(settings_folder / 'server_address.yaml', 'w') as f_w:
        yaml.dump(dic_server, f_w)         #


if __name__ == '__main__':

    set_IP()
    init(app.config)      # clean last processings and upload folders

    with open(settings_folder / 'server_address.yaml') as f_r:
        addr = yaml.load(f_r, Loader=yaml.FullLoader)
    PORT = addr['port']
    HOST = addr['host'] if platf == 'win' else '0.0.0.0'

    print("host is ", HOST)
    launch_browser(PORT, HOST, platf)
    message_at_beginning(HOST, PORT)
    print(Style.RESET_ALL)

    socketio.run(app, port=PORT, host=HOST)
