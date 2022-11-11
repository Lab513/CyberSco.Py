from datetime import datetime
from modules.mda import MDA

class DETECT_RARE_FLUO(MDA):
    '''
    name : detect rare event
    '''
    def __init__(self, ldevices=None):
        '''
        name : Track rare fluorescent cell
        description : cells without fluorescence which are in majority
        are mixed with few cells expressing RFP fluorescence.
        Among the fluorescing cells, one is picked at random and tracked
        (placed in the center of the image and followed by).
        '''
        MDA.__init__(self, ldevices)

    def define(self, debug=[0]):          # make simple rfp pics
        '''
        BF + Tracking rare fluo events,
        '''
        self.focus()                # add refocusing
        self.take_pic()               # add take pic
        self.take_pic_fluo('rfp')     # add take pic fluo
        self.event.name = 'rfp'
        ##
        self.analyse_pic()            # analyse the pic
        self.cond = 'no_condition'    #
        ##
        self.launch_loop()            # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.track_in_analysis = True          # perform tracking
            pos.event = self.event
            pos.first_time = self.first_time
            if pos.event.name:             # same event on all the positions
                pos.event.exists = True

    def init_conditions(self):
        '''
        '''
        self.init_on_positions()
        ##
        self.delay = 1                   # delay between repetitions in min
        self.repeat = 600                # number of repetitions

    def check_conditions(self, rep):
        '''
        '''
        for pos in self.list_pos:
            pos.track_on_event(pos.list_fluo_cells)
