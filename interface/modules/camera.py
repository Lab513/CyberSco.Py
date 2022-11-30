'''
Camera
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_paths import *
from interface.modules.init.init_devices import *

def set_autocontrast(cntrst, debug=[0]):
    '''
    Set the value for autocontrast..
    '''
    print(f'Set autocontrast to {cntrst}')
    with open(settings_folder / 'cam_params.yaml') as f_r:
        dic_cam_params = yaml.load(f_r, Loader=yaml.FullLoader)
    dic_cam_params['autocontrast'] = cntrst
    with open(settings_folder / 'cam_params.yaml', 'w') as f_w:
        yaml.dump(dic_cam_params, f_w)

set_autocontrast(True)       # use autocontrast at the beginning for BF


@socketio.on('autocontrast')
def make_autocontrast(val_cntrst, debug=[0]):
    '''
    Use or not the autocontrast for BF images
    '''
    cntrst = eval(val_cntrst)
    if 0 in debug:
        print(f'cntrst is {cntrst}')
    set_autocontrast(cntrst)
    emit('current_contrast', cntrst)


@socketio.on('new_pic')
def new_pic(msg):
    '''
    Changing the camera image
    '''
    print('take new pic')
    # take a new pic
    ev.take_pic(app.config['PIC_PATH'])


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
