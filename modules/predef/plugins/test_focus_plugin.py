from datetime import datetime
from modules.mda import MDA

class TEST_FOCUS(MDA):
    '''
    Used for tests !!!
    '''
    def __init__(self, ldevices=None, user=None):
        '''
        name : test Focus
        description : simple test for the AFML
        '''
        MDA.__init__(self, ldevices, user=user)

    def define(self, debug=[0]):            # make simple rfp pics
        '''
        testing the autofocus
        '''
        if 0 in debug:
            print('####### Applying define !!! ########')
        ##
        self.focus()                      # add refocusing
        self.take_pic()                   # add take pic
        ##
        self.launch_loop()                # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.track_in_analysis = False
            pos.segm_for_dmd = 'mod1'
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
        self.repeat = 1                       # number of repetitions

    def check_conditions(self, rep):
        '''
        '''
        pass
