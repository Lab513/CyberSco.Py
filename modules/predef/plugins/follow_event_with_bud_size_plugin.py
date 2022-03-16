'''
Follow mitosis event using buds size
'''
from datetime import datetime
from modules.predef.plugins.plugins_funcs.track_obs_fluo import TRACK_OBSERVE_FLUO as TOF
from modules.mda import MDA

class FOLLOW_EVENT_WITH_BUD_SIZE(MDA,TOF):
    '''
    name : Mitosis event imaging
    description : cells are all segmented in real time and only the ones with
    a size comprised between a low and high limit are followed.
    Each of these cells has its growth history registered.
    When a cell reaches the upper area limit, with a sufficient
    speed of growth and enough registered growth points for having
    a good estimation of its speed of growth it is selected as a candidate
    for the tracking step. Among all the candidates, one is chosen at random
    and tracked during twenty minutes with its nucleus observed with RFP
    imaging for observing the mitosis event.
    '''
    def __init__(self, ldevices=None):
        '''

        '''
        MDA.__init__(self, ldevices)
        # Settings Channels used for observation
        self.fluo_obs = 'RFP0'

    def define(self):                                #
        '''

        '''
        self.refocus()                               # add refocusing
        self.take_pic()                              # add take pic
        self.event.name = 'bud_with_size'
        self.cond = 'follow_event_with_segm'
        ##
        self.analyse_pic()                           # analyse the pic
        ##
        self.launch_loop()                           # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.track_in_analysis = True      # using tracking in the experiment
            pos.event = self.event
            pos.first_time = self.first_time
            if pos.event.name:            # same event on all the positions
                pos.event.exists = True
            pos.mature_size = self.mature_size
            pos.trig_min_slope = self.trig_min_slope
            pos.trig_hist_length = self.trig_hist_length

    def init_conditions(self):
        '''
        '''
        # delay before triggering fluo from bud detection moment
        self.delay_trig = 1
        self.obs_time =  20.0            # Observation time in min
        self.list_pos_blocked = []        # positions blocked
        self.delay_obs = 0.5                # delay between each mitosis obs
        # initial delay between main repetitions
        self.delay = self.delay_init = 3
        self.repeat = 600                   # number of repetitions
        # delay in minute after the end of observation
        self.delay_after_obs_end = 10
        ### buds
        self.mature_size = 48               # for 60x
        # minimal slope for triggering the observations
        self.trig_min_slope = 1.0
        # nb of points in the history for triggering
        self.trig_hist_length = 2
        # initialize on each position
        self.init_on_positions()

    def check_conditions(self, rep, debug=[]):
        '''
        '''
        if 1 in debug:
            # current delay between acquisitions
            print(f'In follow_event_with_segm, self.delay = {self.delay}')
        for pos in self.rand_list(self.list_pos) :      # take pos randomly
            if rep == 0:
                # save initial position
                pos.xy_init = pos.list_steps['posxyz'].val
            if 2 in debug:
                 print(f'pos.list_budding_cells is {pos.list_budding_cells}')
            self.track_and_fluo_mess0(pos)
            # find when to trigger the RFP observations
            self.track_and_fluo_prepare_trig(pos)
            # trigger the RFP observations
            self.track_and_fluo_trig_rfp(pos, self.fluo_obs)
            # trigger track if event detected
            pos.track_on_event(pos.list_budding_cells)
            # reinitialize the tracking for mitosis event                         
            self.track_and_fluo_reinit(pos)
