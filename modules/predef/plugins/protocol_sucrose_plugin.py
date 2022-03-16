from datetime import datetime
from modules.mda import MDA

class PROTOCOL_SUCROSE(MDA):
    '''
    Sucrose protocol for observing lag time according to the number of cells..
    '''
    def __init__(self, ldevices=None):
        '''
        name : Sucrose lag experiment
        description : the cells (which are able to use sucrose cooperatively)
        of different chambers are fed with glucose and counted in real time.
        Their supply is then stopped and replaced with sucrose when the number
        of cells reaches a given limit. For each chamber this limit is different.
        The counting continues and it is possible at the end of the
        experiment to observe from the cells counting, the lag phenomenon
        which is  characterized by a time during which the cells do not
        divide or very slowly until being able to exploit cooperatively
        the sucrose.
        '''
        MDA.__init__(self, ldevices)

    def define(self, debug=[0]):
        '''
        '''
        self.refocus()                         # add refocusing
        self.take_pic()                        # add take BF pic
        ##
        self.analyse_pic()                     # analyse the pic
        self.cond = 'sucrose'                  # apply the conditions 2, sucrose
        ##
        self.launch_loop()                     # Loop

    def init_on_positions(self):
        '''
        Initialize the protocol
        '''
        for pos in self.list_pos:
            pos.event = self.event
            pos.first_time = self.first_time
            if pos.event.name:                 # same event on all the positions
                pos.event.exists = True

    def init_conditions(self):
        '''
        Setup parameters and initial conditions
        '''
        self.init_on_positions()
        ##
        lthresh = [100, 500, 2000, 500]       # list of the thresholds
        for i,pos in enumerate(self.list_pos):
            pos.thresh_cells = lthresh[i]               # initial delay
        self.delay = self.delay_init = 2
        self.repeat = 2400                        # number of repetitions

    def check_conditions(self, rep):
        '''
        At a given threshold trigger the sucrose
        '''
        for pos in self.list_pos:
            if pos.nb_cells > pos.thresh_cells and not pos.switched :
                if pos.num_gate:                 # pos.num_gate exists
                    pos.switched = True          # position blocked
                    # adding num gate to self.gates_blocked
                    self.gates_switched += [pos.num_gate]
                    print(f'self.gates_switched'
                       ' {self.gates_switched} for nb cell of {pos.nb_cells} ')
                    #  change gates value
                    self.ga.set_pos_indices(self.gates_switched, 1)
