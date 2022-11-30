from modules.modules_mda.positions import POS
from modules.modules_mda.mda_actions import STEP
import shutil as sh
import oyaml as yaml
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

class PREPARE_MDA():
    '''
    '''

    def __init__(self):
        '''
        '''
        pass

    def save_experim_infos(self):
        '''
        Copy the information about the experiment with the mda results
        '''
        # infos about the experiment
        infos = opj('interface', 'infos_mda', 'experiment_infos.yaml')
        sh.copy(infos, self.dir_mda_temp)

    def save_protocol(self):
        '''
        Copy the protocol in the mda folder
        '''
        # protocol used for the experiment
        prot = opj('interface', 'static', 'mda_protocols', self.curr_prot)
        sh.copy(prot, self.dir_mda_temp)

    def init_positions(self):
        '''
        Create the positions from the interface information
        '''
        self.nb_pos = len(self.lxyz)
        for i in range(self.nb_pos):
            pos = POS(self.ldevices, self.mod0, self.mod1)
            pos.num = i
            pos.dir_mda_temp = self.dir_mda_temp
            pos.mda = self
            # list of the positions in the mda object
            self.list_pos += [pos]
            # retrieve the coordinate of each position..
            pos.init_xyz = self.lxyz[i]
            pos.list_steps = {'posxyz': None, 'refocus': None,
                              'take_pic': None, 'fluo_rfp': None,
                              'fluo_gfp': None}

    def get_positions(self, debug=[0]):
        '''
        Load the positions
        lxyz : list of positions [[x0,y0,z0], [x1,y1,z1]..]
        '''
        self.init_positions()
        for i, xyz in enumerate(self.lxyz):
            print(f'i: {i}')
            print(f'xyz: {xyz}')
            # ref_posz for the AF
            self.list_pos[i].ref_posz = xyz[2]
            # xy = [posx,posy]
            self.list_pos[i].list_steps['posxyz'] = STEP(xyz, kind='posxyz')
            if 0 in debug:
                print(f'In mda.get_positions,\
                      self.list_pos[i].ol.ref_posz'
                      f' = {self.list_pos[i].ref_posz} ')

    def prepare_channels(self, dic_chan_set):
        '''
        Apply the Cooled "settings channels" from the interface values
        '''
        self.co.prepare_channels(dic_chan_set['COOL'])

    def get_chan_set(self):
        '''
        Load dic_chan_set for the channels settings
        '''
        print(f'#### self.list_SC_ET is {self.list_SC_ET}')
        for i, pos in enumerate(self.list_pos):
            try:
                # load chan set for each pos
                pos.chan_set = self.list_SC_ET[i]
            except:
                pos.chan_set = None

    def get_gates(self):
        '''
        Load the gate Id for each position
        '''
        print(f'#### self.list_gates is {self.list_gates}')
        for i, pos in enumerate(self.list_pos):
            try:
                # give a value to attribute gate
                pos.num_gate = int(self.list_gates[i])
            except:
                pos.num_gate = None

    def get_focus(self,debug=[1]):
        '''
        Retrieve the kind of focus
        '''
        try:
            for i, pos in enumerate(self.list_pos):
                # attach focus method to position
                pos.kind_focus = self.list_AF[i][0]
                pos.step_focus = self.list_AF[i][1]
                pos.delta_focus = self.list_AF[i][2]
                pos.focus_nbsteps = self.list_AF[i][3]
                pos.thresh = self.list_AF[i][4]
                print(f'pos.kind_focus is {pos.kind_focus}')
                # attach the kind of AFML to the position
                # even if not used..
                pos.ol.afml_optim = self.afml_optim
        except:
            print('Cannot retrieve AF information.. ')
        if 1 in debug:
            print('When get_focus is done, ')
            for pos in self.list_pos:
                print(f'pos.kind_focus is {pos.kind_focus}')
