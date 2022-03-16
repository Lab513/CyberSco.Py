'''
Stop rebegin sucrose experiment
'''
from datetime import datetime
from modules.mda import MDA

class PROTOCOL_SUCROSE(MDA):
    '''
    name : observing sucrose lag time
    '''
    def __init__(self, ldevices=None):
        '''
        name : Cell density synchronization
        description : the cells of different chambers
        are counted in real time and their glucose supply
        is stop at a given number of cells.
        When all the chambers have no more glucose supply,
        glucose supply is triggered again
        '''
        MDA.__init__(self, ldevices)

    def define(self, debug=[0]):      # make simple rfp pics
        '''
        Sucrose protocole
        '''
        self.refocus()                         # add refocusing
        self.take_pic()                        # add take pic
        ##
        self.analyse_pic()                     # analyse the pic
        self.cond = 'sucrose'                  # apply the conditions 2, sucrose
        ##
        self.launch_loop()                     # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.event = self.event
            pos.first_time = self.first_time
            if pos.event.name:                # same event on all the positions
                pos.event.exists = True

    def init_conditions(self):
        '''
        '''
        self.init_on_positions()
        ##
        self.num_plat = 0                    # initial plateau index
        self.lthr_cells = [200, 400, 700, 1000, 1300]      # thresholds list
        self.plateau_duration = 60               # plateau duration in minutes

    def reaching_plateau(self):
        '''
        thresh_cells : threshold for plateau
        '''
        for pos in self.list_pos:
            if pos.nb_cells > self.lthr_cells[self.num_plat] and not pos.blocked :
                if pos.num_gate:                      # pos.num_gate exists
                    pos.blocked = True                    # position blocked
                    # adding num gate to self.gates_blocked
                    self.gates_blocked += [pos.num_gate]
                    print(f'self.gates_blocked {self.gates_blocked}')
                    # change gates value
                    self.ga.set_pos_indices(self.gates_blocked, 1)
                    # all gates blocked
                    if len(self.gates_blocked) == self.nb_pos:
                        # time at which all the gates where blocked
                        self.time_blocked = datetime.now()

    def reinit_for_next_plateau(self):
        '''
        At the end of the plateau, reinitialize the variables
        '''
        self.gates_blocked = []       # reinitialize list of gates blocked
        if self.num_plat < len(self.lthr_cells) - 2:
            self.num_plat += 1             # passing to the next plateau
        for pos in self.list_pos:
            pos.blocked = False            # unblock the positions

    def plateau_and_rebegin(self):
        '''
        Make the plateau and rebegin after the plateau duration delay
        '''
        if len(self.gates_blocked) == self.nb_pos:
            t_from_blocked = (datetime.now() - self.time_blocked).seconds
            print(f'time_from_tblocked {t_from_blocked} sec')
            # plateau duration in minutes
            if t_from_blocked > 60*self.plateau_duration :
                # glucose in the pipes                    
                self.ga.set_pos_indices(self.gates_blocked, 0)
                self.reinit_for_next_plateau()

    def check_conditions(self, rep):
        '''
        '''
        self.reaching_plateau()
        self.plateau_and_rebegin()
