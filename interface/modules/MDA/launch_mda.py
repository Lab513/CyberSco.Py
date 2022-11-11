'''
Launch MDA
'''

from interface.modules.init.init_params import *
from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
from interface.modules.MDA.infos_mda import *
from interface.modules.MDA.predefined_mda import *
from interface.modules.MDA.tree_mda import *
from interface.modules.camera import *
import interface.modules.init.init_glob_vars as g


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
    g.mda_launched = True
    g.mda_time_start = time()
    print(f'In launch_mda, g.mda_launched is {g.mda_launched}')
    emit('close_cam', '')          # close cam to access it for the protocol
    emit('modif_interf', '')       # modify the interface


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


@socketio.on('make_mda')
def make_mda(msg):
    '''
    Launch the MDA
    '''
    # time for live cam to shut down properly
    sleep(10)
    ##
    # retrieve infos about the mda experiment
    ask_experim_infos()
    # retrieve infos about how to monitor the experiment
    ask_for_monitor_params()
    ##
    sleep(2)
    ##
    # choosing beetween Evolv and Zyla
    cam = cam_choice()
    # attaching the camera to the µscope for focus
    ol.cam = cam
    ##
    if predefined_mda:
        launch_mda_predef(cam)
    else:
        launch_mda_tree(cam)
