'''
HOG1 experiment, sample faster when the events occur for
capturing the signal with a good temporal resolution..
'''
from datetime import datetime
from modules.mda import MDA, STEP

class SIMPLE_OSMOSTRESS(MDA):
    '''
    name : HOG1-GFP response to osmotic shock
    description : the cells are fed with glucose and a picture is taken every 5 minutes.
    After 30 minutes, an osmotic shock is produced with sorbitol.
    The observation rate is changed to 15 seconds during 4  minutes,
    then to every minute during 20 minutes,  then the sorbitol is stopped,
    the rate lowered to every 5 mintues and a new cycle rebegins
    60 minutes after the previous osmotic shock
    '''
    def __init__(self, ldevices=None):
        '''

        '''
        MDA.__init__(self, ldevices)

    def define(self):                         #
        '''
        '''
        self.refocus()                               # add refocusing
        self.take_pic()                              # add take pic
        self.take_pic_fluo('rfp')                    # add take pic RFP
        self.take_pic_fluo('gfp')                    # add take pic GFP
        ##
        self.analyse_pic()                           # analyse the pic
        self.cond = 'hog1'                           #
        ##
        self.launch_loop()                           # Loop

    def init_on_positions(self):
        '''
        '''
        for pos in self.list_pos:
            pos.track_in_analysis = True
            pos.event = self.event
            pos.first_time = self.first_time
            if pos.event.name:                 # same event on all the positions
                pos.event.exists = True

    def init_conditions(self):
        '''
        '''
        self.init_on_positions()
        ##
        for pos in self.list_pos:
            pos.curr_exp = 'hog1'
        self.gatepulse = 1                      # gate used for the pulses
        self.first_time = datetime.now()        # origin of clock
        # delay between measurements for fast observation
        self.delay_obs0 = 0.25
        self.offset_obs0 = 0                    # triggering in advance
        # delay between measurements for fast observation
        self.delay_obs1 = 1
        self.per_pulse = 60                       # pulses period
        self.time_obs0 = 5                        # observation time in min
        self.time_obs1 = 25                       # observation time in min
        # 3 min precision for triggering the event
        self.max_trig_time = 3
        self.phi = self.per_pulse/2               # dephasing
        self.delay_init = 5            # delay of observation at the beginning
        self.delay = self.delay_init
        self.repeat = 1200             # number of total repetitions

    def check_conditions(self, rep, debug=[]):
        '''
        regularly_trig_osmo_obs
        Every 30 min, 6 min BF, make osmotic schock,
        observe during 15 min every 30 sec
        and go back to 6 min BF
        '''
        # current time
        curr_time_min = int((datetime.now() - self.first_time).seconds/60)

        #--------------------- fast and osmotic shock

        # begin the observations fast
        # trigger observations
        if (curr_time_min + self.phi +
                self.offset_obs0)%self.per_pulse < self.delay:
            print(f'**** Begin the observations at {curr_time_min} min ****')
            self.delay = self.delay_obs0          # passing to faster frequency
            for pos in self.list_pos:
                pos.list_steps['refocus']  = None             # remove focus

        # Create and osmotic pulse

        # trigger the pulse..
        if (curr_time_min > self.per_pulse/6) and ((curr_time_min +
                            self.phi)%self.per_pulse < self.delay) :
            print(f'**** send a pulse at {curr_time_min} min !!! ****')
            self.ga.set_pos_indices([self.gatepulse], 1)

        #---------------------  medium

        # End of fast sampling, medium rate

        if (curr_time_min > self.phi) and (curr_time_min + self.phi
                            - self.time_obs0)%self.per_pulse < self.delay:
            print(f'**** Return to medium sampling at {curr_time_min} min ****')
            # repassing to slow frequency
            self.delay = self.delay_obs1
            for pos in self.list_pos:
                # restablishing the focus
                pos.list_steps['refocus'] = STEP(None, kind='refocus')

        #--------------------- stop medium and stop osmotic shock

        # End of medium sampling, slow rate

        if (curr_time_min > self.phi) and (curr_time_min + self.phi
                            - self.time_obs1)%self.per_pulse < self.delay:
            print(f'**** Return to slow sampling at {curr_time_min} min ****')
            # repassing to slow frequency
            self.delay = self.delay_init

        # End of osmotic pulse (after 30min)

        # closing the gate
        if (curr_time_min > self.phi) and (curr_time_min%self.per_pulse < self.delay):
            print(f'**** Remove osmotic schock at {curr_time_min} min ****')
            self.ga.set_pos_indices([self.gatepulse], 0)
