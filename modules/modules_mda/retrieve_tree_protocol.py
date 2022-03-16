'''
Passing from tree to mda
'''

import oyaml as yaml
from pathlib import Path
from colorama import Fore, Style      # Color in the Terminal

import os
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join

try:
    from modules_mda.loop import LOOP
    from modules_mda.positions import POS
except:
    from modules.modules_mda.loop import LOOP
    from modules.modules_mda.positions import POS


class RETRIEVE_TREE_PROTOCOL():
    '''
    mda protocol tree
    '''
    def __init__(self):
        '''
        '''
        self.settings_folder = Path('interface') / 'settings'

    def retrieve_position(self, d, obj, debug=[]):
        '''
        From tree to mda object for position
        '''
        if 0 in debug:
            print('dealing with position')
            print(f'###** d is {d} ')
        pos = POS(self.ldevices, self.curr_mod, title=d['title'])
        pos.dir_mda_temp = self.dir_mda_temp
        pos.first_time = self.first_time
        ##
        pos.tree_id = d['key']
        ##
        # retrieving pos from the tree
        pos.x, pos.y, pos.z = float(d['data']['xPosition']),\
            float(d['data']['yPosition']), float(d['data']['zPosition'])
        ##
        pos.gate = d['data']['gate']
        if 1 in debug:
            print(f'pos.x, pos.y, pos.z are {pos.x, pos.y, pos.z}....')
        if pos.x != 0 and pos.y != 0:
            pos.list.append(pos.goto_xy)  # x,y position
        pos.ol.kind_focus = self.kind_focus     # kind focus from mda to pos
        pos.ol.afml_optim = self.afml_optim     # optim metho from mda to pos
        pos.ref_posz = pos.z                    # position reference for afml
        ##
        obj.list.append(pos)
        ## retrieving predefined parameters
        self.lpos_id.append(pos.tree_id)
        self.lxyz.append([pos.x, pos.y, pos.z])     # list_pos for predefined
        self.list_gates.append(pos.gate)          # list_gate for predefined
        # list of the Settings channels with exposition time..
        self.list_SC_ET.append([])
        ##
        self.iterdict(pos, d['children'])

    def retrieve_take_picture(self, d, obj, mask, debug=[]):
        '''
        From tree to mda object for take_picture
        '''
        if 0 in debug:
            print('dealing with SPSC')
            print(f'### d is {d} ')
            print(f"d['data']['setting_channel_name'] "
                  f" {d['data']['setting_channel_name']}")
        SC_name = d['data']['setting_channel_name']         # Settings channels
        exp_time = int(d['data']['exposure_time'])          # exposure time
        print(f'*** SC_name is {SC_name} *** ')
        print(f'*** Exposure time is {exp_time} *** ')
        if mask:
            name_mask = d['data']['mosaic_mask_name']       # mask name
            print(f'*** mask name is {name_mask} *** ')
            # mask time of exposure
            mask_exp_time = d['data']['mask_exposure_time']
            print(f'*** mask_exp_time is {mask_exp_time} *** ')
        try:
            addr_SC = self.settings_folder /\
                    'settings_channels' / f'{SC_name}.yaml'
            print(f'addr_SC is {addr_SC} ')
            with open(addr_SC) as f_r:                             # current SC
                set_chan = yaml.load(f_r, Loader=yaml.FullLoader)
        except:
            print(f'No SC with name {SC_name} !!!')
        if SC_name == 'BF':
            # take a picture  in BF
            obj.list.append([obj.taking_picture, exp_time])
        # fluo
        elif SC_name != 'BF' and not mask:
            # take a picture  in fluorescence
            print('Simple fluo')
            obj.list.append([obj.taking_picture_fluo, set_chan, exp_time])
        else:
            # take a picture  in fluorescence with DMD
            print(' obj.list with mask for DMD !!! ')
            print(f' In retrieve tree protocol, using name_mask {name_mask} ')
            obj.list.append([obj.taking_picture_fluo, set_chan,
                             exp_time, name_mask, mask_exp_time])
        # add SC and ET to mda.list_SC_ET
        self.list_SC_ET[-1].append({'name': SC_name,
                                    'exp_time': exp_time})

    def retrieve_loop(self, d, obj, debug=[0]):
        '''
        From tree to mda object for loop
        '''
        if 0 in debug:
            print('dealing with Loop')
            print(f'### d is {d} ')
        nb_rep, delay = d['data']['nb_repetition'],\
            d['data']['time_per_repetition']
        print(Fore.GREEN + f'### nb_rep {nb_rep}, '
                    ' time per repetition {delay} min ')
        print(Style.RESET_ALL)
        loop = LOOP(nb_rep, delay)
        obj.list.append(loop)
        self.iterdict(loop, d['children'])

    def retrieve_AF(self, d, obj, debug=[0]):
        '''
        From tree to mda object for Autofocus
        '''
        if 0 in debug:
            print('dealing with Autofocus')
        obj.list.append(obj.refocus)                # make the Autofocus
        try:
            obj.offset = d['data']['zoffset']           # offset from the tree
        except:
            obj.offset = 0
            print('Offset not defined in the interface, set to 0')
        self.loffsets.append(obj.offset)      # list of offsets for predefined
        # kind of focus, possible values: zdc, afml_sweep, afml_dich
        try:
            obj.kind_focus = d['data']['select_AF']
        except:
            print(f"d['data']['select_AF'] not defined")
            print('setting to default value: afml_sweep')
        obj.kind_focus = 'afml_sweep'      # default value for AF

        # list of kind of AF for predefined
        self.list_AF.append(obj.kind_focus)
        if 1 in debug:
            print(f'self.list_AF is {self.list_AF}')

    def retrieve_protocol(self, d, obj, debug=[0]):
        '''
        From tree to mda object for Protocol
        '''
        if 0 in debug:
            print('dealing with Protocol')
            print(f'### d is {d} ')
        obj.title = d['title']

    def retrieve_root(self, d, obj, debug=[]):
        '''
        From tree to mda object for Root
        '''
        if 2 in debug:
            print('dealing with root')
        self.iterdict(obj, d['children'])
