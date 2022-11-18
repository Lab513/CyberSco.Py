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
        pos = POS(self.ldevices, self.curr_mod,
                  self.ev_mod, title=d['title'])
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
        #pos.ol.kind_focus = self.kind_focus     # kind focus from mda to pos
        pos.ol.afml_optim = self.afml_optim     # optim method from mda to pos
        pos.ref_posz = pos.z                    # position reference for afml
        ##
        obj.list.append(pos)
        ## retrieving predefined parameters
        self.make_lists_for_predef(pos)
        ##
        self.iterdict(pos, d['children'])

    def make_lists_for_predef(self, pos):
        '''
        Lists from the Tree for predef experiments
        '''
        self.lpos_id.append(pos.tree_id)
        self.lxyz.append([pos.x, pos.y, pos.z])     # list_pos for predefined
        self.list_gates.append(pos.gate)          # list_gate for predefined
        # list of the Settings channels with exposition time..
        self.list_SC_ET.append([])
        # self.list_AF.append(pos.kind_focus)

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

    def retrieve_loop(self, d, obj, debug=[]):
        '''
        From tree to mda object for loop
        '''
        if 0 in debug:
            print('dealing with Loop')
            print(f'### d is {d} ')

        nb_rep, delay = d['data']['nb_repetition'],\
                        d['data']['time_per_repetition']
        if 1 in debug:
            print(Fore.GREEN + f'\n### nb_rep {nb_rep}, '
                        f' time per repetition {delay} min ')
            print(Style.RESET_ALL)
        loop = LOOP(nb_rep, delay)
        obj.list.append(loop)
        self.iterdict(loop, d['children'])

    def retrieve_AF(self, d, obj, debug=[0,1,2]):
        '''
        From tree to mda object for Autofocus
        obj = POS()
        '''
        if 0 in debug:
            print('dealing with Autofocus')
        # make the Autofocus
        obj.list.append(obj.refocus)
        try:
            # offset from the tree
            obj.offset = d['data']['zoffset']
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

        if obj.kind_focus == None: # select_AF = null in the tree by default..
            obj.kind_focus = 'afml_sweep'

        if 1 in debug:
            print(f'obj.kind_focus = {obj.kind_focus}')
            # list of kind of AF for predefined
            print(f'self.list_AF before is {self.list_AF} !!!')

        if obj.kind_focus == 'afml_sweep':
            obj.focus_nbsteps = int(d['data']['nb_steps_afml'])
            step_width = float(d['data']['step_afml'])
            thresh = int(d['data']['thresh'])
            obj.delta_focus = round(obj.focus_nbsteps*step_width*50,2)
            obj.step_focus = int(2*obj.delta_focus / obj.focus_nbsteps)
            obj.thresh = thresh
            if 2 in debug:
                print(f'#####  obj.step_focus = {obj.step_focus}')
                print(f'#####  obj.focus_nbsteps = {obj.focus_nbsteps}')
                print(f'#####  obj.thresh = {obj.thresh}')
            self.list_AF += [ [obj.kind_focus, obj.step_focus,
                              obj.delta_focus, obj.focus_nbsteps,
                              obj.thresh] ]
        else:
            self.list_AF += [ [obj.kind_focus] ]
        if 1 in debug:
            print(f'self.list_AF after is {self.list_AF}')

    def retrieve_delay(self, d, obj, debug=[0]):
        '''
        Delay in the protocol
        '''
        delay = int(d['data']['time'])
        if 0 in debug:
            print(f'in retrieve_tree delay is {delay}')
        obj.list.append([obj.delay, delay])

    def retrieve_protocol(self, d, obj, debug=[]):
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
