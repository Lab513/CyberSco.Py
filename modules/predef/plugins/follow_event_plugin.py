from datetime import datetime
from modules.predef.plugins.plugins_funcs.track_obs_fluo import TRACK_OBSERVE_FLUO as TOF
from modules.mda import MDA

class FOLLOW_EVENT(MDA,TOF):
    '''
    name : follow event
    '''
    def __init__(self, ldevices=None):
        '''
        '''
        MDA.__init__(self, ldevices)
        # Settings Channels used for observation
        self.fluo_obs = 'RFP0'

    def define(self):
        '''

        '''
        self.focus()                       # add refocusing
        self.take_pic()                      # add take pic
        self.event.name = 'bud'
        ##
        self.analyse_pic()                   # analyse the pic
        self.cond = 'follow_event'           #
        ##
        self.launch_loop()                   # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.track_in_analysis = True
            pos.event = self.event
            pos.first_time = self.first_time
            if pos.event.name:                # same event on all the positions
                pos.event.exists = True

    def init_conditions(self):
        '''
        '''
        self.init_on_positions()
        ##
        for pos in self.list_pos:
            # trigger all buds observation with size
            pos.segm_all_buds = True
        # delay before triggering fluo from bud detection moment
        self.delay_trig = 4
        self.obs_time = 5               # Observation time in min
        self.list_pos_blocked = []      # positions blocked
        self.delay_obs = 0.5            # delay between each mitosis obs
        self.delay_init = 1             # initial delay
        self.delay = self.delay_init
        self.repeat = 200               # number of repetitions

    def check_conditions(self, rep, debug=[]):
        '''
        '''
        for pos in self.rand_list(self.list_pos) :         # take pos randomly
            self.track_and_fluo_mess0(pos)
            # find when to trigger the RFP observations
            self.track_and_fluo_prepare_trig(pos)
            # trigger the RFP observations
            self.track_and_fluo_trig_rfp(pos, self.fluo_obs)
            # trigger track if event detected
            pos.track_on_event(pos.list_budding_cells)
            # reinitialize the tracking of mitosis event
            self.track_and_fluo_reinit(pos)
