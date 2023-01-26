from datetime import datetime
from modules.mda import MDA

class TEST_RANDZ(MDA):
    '''
    Used for tests !!!
    '''
    def __init__(self, ldevices=None, user=None):
        '''
        name : test random z
        description : simple test for assessing the AFML robustness
        '''
        MDA.__init__(self, ldevices, user=user)

    def define(self, debug=[0]):
        '''

        '''
        if 0 in debug:
            print('####### Applying define !!! ########')
        ##
        self.focus()                         # add refocusing
        self.take_pic()                      # add take pic
        ##
        self.launch_loop()                   # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.track_in_analysis = False
            pos.event = self.event
            pos.first_time = self.first_time
            pos.randz = []
            if pos.event.name:                 # same event on all the positions
                pos.event.exists = True

    def init_conditions(self):
        '''
        '''
        self.init_on_positions()
        ##
        self.delay = 1                         # delay between repetitions in min
        self.repeat = 60                       # number of repetitions

    def check_conditions(self, rep):
        '''
        Change the position at random un x and y
        '''
        for pos in self.list_pos:
            pos.random_z(2)                 # random step in x,y
        pass
