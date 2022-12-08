'''
Snap and live
'''

from modules.modules_mda.take_pic_fluo_or_BF import TAKE_PIC_FLUO_OR_BF as TPFB
from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
from modules.modules_mda.make_video import MAKE_VIDEO as MV
from threading import Thread
from time import sleep
# take picture fluo or bf for SNAP
tpfb = TPFB(ol, co, emit)

snap_addr = None
live_reg = 'off'
stop_movie = False
mv = MV(snap=True)


def register_movie():
    '''
    Take pictures for the movie
    '''
    global stop_movie
    num = 0
    while 1:
        sleep(1)
        tpfb.take_pic(None, snap_addr=snap_addr, kind_tag='num', num=num)
        num += 1
        if stop_movie:
            break
    stop_movie = False


@socketio.on('snap')
def snap(snap_val):
    '''
    Snap, Take an image online
    '''
    global stop_movie, live_reg
    # take snap picture at address snap_addr..
    print(f'Taking a snap and saving it at address {snap_addr}')
    if not tpfb.live_cam:
        tpfb.take_pic(snap_val, snap_addr=snap_addr)
        emit('snap_overview', '')
    else:
        # register the movie
        if live_reg == 'off':
            thread_live_movie = Thread(target=register_movie)
            thread_live_movie.start()
            emit('save_movie', '')
            live_reg = 'on'
        else:
            # stop registering the movie
            stop_movie = True
            emit('stop_saving_movie', '')
            live_reg = 'off'
            # make a video with the pics at addr snap_addr
            mv.size = 512
            mv.create_video( prefix='snap',
                             name_folder = snap_addr,
                             name_movie=f'movie_snap_{tpfb.date()}.avi',
                             erase_imgs=True )


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
    tpfb.live_cam = True


@socketio.on('live_fluo_off')
def live_fluo_off(msg):
    '''
    Set live fluo off
    '''
    tpfb.return_to_BF()
