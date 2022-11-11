'''
Snap and live
'''

from modules.modules_mda.take_pic_fluo_or_BF import TAKE_PIC_FLUO_OR_BF as TPFB
from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
# take picture fluo or bf for SNAP
tpfb = TPFB(ol, co, emit)


snap_addr = None

@socketio.on('snap')
def snap(snap_val):
    '''
    Snap, Take an image online
    '''
    # take snap picture at address snap_addr..
    print(f'Taking a snap and saving it at address {snap_addr}')
    tpfb.take_pic(snap_val, snap_addr=snap_addr)
    emit('snap_overview', '')


@socketio.on('snap_exp_time')
def snap_exp_time(snap_time, debug=[]):
    '''
    Snap exposure time
    '''
    if 0 in debug:
        print(f'snap_time is {snap_time}')
    emit('send_exp_time', snap_time)


@socketio.on('snap_addr')
def snap_addr(new_snap_addr, debug=[]):
    '''
    Snap address
    '''
    global snap_addr
    snap_addr = new_snap_addr
    # save in database
    current_user.snap_addr = snap_addr
    db.session.commit()
    if snap_addr == 'Downloads':
        snap_addr = None
    if 0 in debug:
        print(f'snap_addr is {snap_addr}')
    # emit('send_snap_addr', snap_addr)


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
