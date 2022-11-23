'''
Mda experiments
'''

from time import sleep
from datetime import datetime
from pathlib import Path
from flask_socketio import emit
import shutil as sh
import oyaml as yaml


from modules.util_server import find_platform, chose_server
from modules.util_misc import *

from modules.modules_mda.mda_actions import MDA_ACTIONS as MAC
from modules.modules_mda.prepare_mda import PREPARE_MDA as PRM
from modules.modules_mda.event import EVENT
from modules.modules_mda.positions import POS
from modules.modules_mda.folders import FOLDERS as FOL
from modules.modules_mda.load_models import LOAD_MODELS as LM
from modules.modules_mda.predef_mda import PREDEF_MDA as PDM
from modules.modules_mda.utils import UTILS as UT
from modules.modules_mda.mda_tree_protocol import MDA_TREE_PROTOCOL as MTP

import sys
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

platf = find_platform()
server = chose_server(platf)


class MDA(POS, MTP, LM, FOL, PRM, MAC, PDM, UT):
    '''
    Mda experiment
    '''
    def __init__(self, ldevices=None, user=None, title=''):
        '''
        ldevices : camera, gates, microscope, stage, fluorescence lights
        user : CyberScopy user registered when entering the software.
        '''
        MTP.__init__(self)
        PDM.__init__(self, server=server)
        self.user = user                  # CyberScoPy user..
        self.list_pos = []                # list of positions
        self.lpos_id = []                 # list of the ids for the positions
        self.lxyz = []                    # list for predefined pos
        self.loffsets = []                # list of the offsets for ZDC
        self.list_gates = []              # list of the gates
        self.list_SC_ET = []              # list for settings channel and exposure time
        self.list_AF = []                 # of the kind of autofocuses
        self.ldevices = ldevices          # list of the devices
        self.folder_exp()                 # folders for experiment
        self.logfile()                    # save stdout in logfile
        # self.load_main_model()            # load current model
        # self.load_event_model()           # load event model
        self.load_used_models()
        self.gates_blocked = []
        self.gates_switched = []
        self.load_addr_mails()            # load the mails addresses
        self.ga = self.ldevices[4]        # object gate in mda
        self.co = ldevices[3]             # Cooled
        self.se = ldevices[5]             # Sensors
        self.event = EVENT()
        self.cond = None
        # self.freq_messages = 20      # number of minutes between each message
        self.list_trig_obs = []
        self.list = []
        self.title = title
        self.kind_focus = 'afml_sweep'       # type of focus used

    ##########  Simple tree MDA protocol..

    def loop(self, debug=[0,1]):
        '''
        MDA loop, Tree Protocol
        '''
        # save the informations about the experiment
        if 0 in debug:
            print('In loop, save the infos about the experiment')
        self.save_experim_infos()
        # save the protocol
        if 1 in debug:
            print('In loop, save the protocol')
        self.save_protocol()
        print(f'Current protocol is  : {self.title} ')
        # launching the main loop
        if 2 in debug:
            print(f'In mda.py, self.list is {self.list[0].list}')
            print(f'len(self.list) = {len(self.list[0].list)}')
        self.init_nb_pos(len(self.list[0].list))
        # launch the protocol
        self.list[0].loop(self.dir_mda_temp,
                          self.dir_mda_temp_dash,
                          self.monitor_params,
                          self.event)
