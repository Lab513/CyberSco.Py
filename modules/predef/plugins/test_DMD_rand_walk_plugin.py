from datetime import datetime
from modules.mda import MDA

class TEST_DMD_RAND_WALK(MDA):
    '''
    Used for tests !!!
    '''
    def __init__(self, ldevices=None, user=None):
        '''
        name : mosaic test ML random walk
        description : simple test for the mosaic
                      BF then picture with the Mosaic using a segmentation
                      and finally a random step
        '''
        MDA.__init__(self, ldevices, user=user)

    def define(self, debug=[0]):            # make simple rfp pics
        '''
        Target cells with mosaic
        '''
        if 0 in debug:
            print('####### Applying define !!! ########')
        ##
        self.focus()                         # add refocusing
        self.take_pic()                      # add take pic
        self.analyse_pic()                   # analyse the pic
        self.take_pic_fluo('xcite',
                            mask='segm',
                            mask_exp_time=5)

        ##
        self.launch_loop()                   # Loop

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
        self.repeat = 5                       # number of repetitions

    def check_conditions(self, rep):
        '''
        '''
        for pos in self.list_pos:
            pos.random_step(10)                 # random step in x,y
        pass
