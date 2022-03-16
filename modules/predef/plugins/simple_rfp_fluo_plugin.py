from datetime import datetime
from modules.mda import MDA

class SIMPLE_RFP_FLUO(MDA):
    '''
    Used for tests !!!
    '''
    def __init__(self, ldevices=None):
        '''
        name : simple BF
        '''
        MDA.__init__(self, ldevices)

    def define(self, debug=[0]):            # make simple rfp pics
        '''
        Simple make RFP fluo + BF,
        '''
        if 0 in debug: print('####### Applying define !!! ########')
        ##
        self.refocus()                    # add refocusing
        self.take_pic()                   # add take pic
        self.take_pic_fluo('rfp')         # add take pic fluo
        ##
        self.analyse_pic()                # analyse the pic
        ##
        self.launch_loop()                # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.track_in_analysis = True
            pos.event = self.event
            pos.first_time = self.first_time
            if pos.event.name:               # same event on all the positions
                pos.event.exists = True

    def init_conditions(self):
        '''
        '''
        self.init_on_positions()
        ##
        self.delay = 1                        # delay between repetitions in min
        self.repeat = 400                     # number of repetitions

    def check_conditions(self, rep):
        '''
        '''
        pass
