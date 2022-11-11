'''
Objective
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *


def sending_objective(debug=[]):
    '''
    Send to the interface, the current objective value
    '''
    curr_obj = ol.ask_objective()
    emit('curr_objective', curr_obj, broadcast=True)
    if 1 in debug:
        print(f'sent the current objective {curr_obj} to the interface..')


@socketio.on('change_obj')
def change_objective(obj, debug=[]):
    '''
    Select a new objective
    '''
    ol.select_obj(obj)
    if 0 in debug:
        print(f'Changed objective to {obj}')
