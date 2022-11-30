'''
Init system
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *

from interface.modules.MDA.predefined_mda import *
from interface.modules.MDA.tree_mda import *
from interface.modules.setting_channels import *
from interface.modules.DMD.dmd import *
from interface.modules.objective import *
from interface.modules.ML.models import *
from interface.modules.move_xyz import *
# from interface.modules.page_interf.index import *

from modules.util_misc import *


def init_system(debug=[]):
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
        if 1 in debug:
            print('Init Xcite')
        xc.init_XCite()
        test_xcite(xc)
        if 1 in debug:
            print('XCite init done')
    except:
        if 2 in debug:
            print('Cannot initialize XCite')
    try:
        ga.init_gate(100000)      # init all the LEDs off
    except:
        if 2 in debug:
            print('Cannot init gate..')


# try:
init_system()
# except:
#     print('Cannot initialize..')


state_devices = {}


def devices_connected(debug=[]):
    '''
    Send the informations concerning the devices connexion..
    '''
    global state_devices
    if 0 in debug:
        print('### devices_connected ')
    for device in [pr, ol, co, xc, ga, se]:
        state = f'{device.name}:{device.state}'
        state_devices[device.name] = device.state
        if 0 in debug:
            print(f'state to be sent is  {state} ')
        sleep(0.1)
        emit('connexion_state', state, broadcast=True)
    if 1 in debug:
        print(f'### state_devices is {state_devices}')


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


def sending_ip():
    '''
    Send the Ip for the camera
    '''
    global ip
    ip = socket.gethostbyname(socket.gethostname())
    emit('ip_used', ip, broadcast=True)


def sending_snap_addr():
    '''
    Send the Ip for the camera
    '''
    snap_addr = current_user.snap_addr
    emit('init_snap_addr', snap_addr, broadcast=True)


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
    sending_snap_addr()         # snap address
    # sending initial position information to the client
    double_sending_pos()
    devices_connected()         # connected devices
    infos_hard_soft()           # infos about GPU and ML framework
