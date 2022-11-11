'''
SWEEP CHIP
'''

from interface.run import server
from interface.modules.tools.sweep import SWEEP
from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
from interface.modules.init.init_params import *
from interface.modules.server import *
from interface.modules.move_xyz import *


# sweeping tool
swp = SWEEP(pr, ol, dic_displ_obj, emit, server)

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
