import random
from colorama import Fore, Back, Style                                           # Color in the Terminal
from time import time
from modules.mda import STEP

class TRACK_OBSERVE_FLUO():
    '''
    '''
    def __init__(self):
        '''
        '''
    def reinit_track_event(self, pos, debug=[1,2]):
        '''
        Reinitialize
        '''
        if 1 in debug: print('### reinit_track_event')
        self.delay = self.delay_init                                              # back to the initial delay
        pos.tracking = False                                                      # remove the  tracking
        pos.event.happened = False                                                # reinit event
        self.list_pos_blocked.remove(pos.num)                                   # unblock this position
        pos.list_budding_cells = []
        if 2 in debug:
            print(f'pos.list_budding_cells is {pos.list_budding_cells}')

    def track_and_fluo_reinit(self, pos, debug=[1,2]):
        '''
        Reinitialize the attributes of the position
        '''
        try:
            rep_reinit = pos.reptrig + int((self.obs_time + self.delay_after_obs_end)/self.delay)        # index of iteration when to reinitialize after observation
            rep_reinit_obs = pos.reptrig + int((self.obs_time)/self.delay)        # index of iteration when to reinitialize after observation
            if 2 in debug:
                print(f'pos.reptrig = {pos.reptrig}')
                print(f'self.obs_time = {self.obs_time}')
                print(f'self.delay = {self.delay}')
            if pos.rep == rep_reinit_obs:
                pos.list_steps['fluo_rfp'] = None                                 # remove the fluo observation after self.obs_time
            if pos.rep == rep_reinit:                                             # if observation is finish, reinitialize tracking
                pos.list_steps['posxyz'].val = pos.xy_init                               # return to initial position
                if 1 in debug: print(f'Reinitialize at rep = {rep_reinit}')
                self.reinit_track_event(pos)
                if self.cond == 'follow_event_with_segm':
                    pos.reinit_buds_hist()                                        # for buds with size, reinitialize the histories
        except:
            print('no pos.reptrig yet !!!')

    def track_and_fluo_add_trig_nb_rep(self, pos):
        '''
        change the rate and determine the number of repetitions before observation..
        '''
        self.delay = self.delay_obs                                               # faster frequency (in minute)
        pos.reptrig = pos.rep + max(int(self.delay_trig/self.delay),1)        # index at which to trigger after mature bud detection
        self.list_trig_obs += [pos.rep + int(self.obs_time/self.delay)]       # list of the rep values for trigger
        print(f'pos.reptrig is {pos.reptrig} !!!')
        self.list_pos_blocked.append(pos.num)                                   # block the position

    def track_and_fluo_prepare_trig(self, pos, debug=[1]):
        '''
        Set time for triggering RFP observations
        '''
        if 1 in debug: print(f'pos.list_budding_cells {pos.list_budding_cells} , pos.tracking {pos.tracking} ')
        if pos.list_budding_cells and not pos.tracking:                           # if buds detected and not tracked yet
            if pos not in self.list_pos_blocked:                                  # position is not blocked
                if self.list_trig_obs:                                            # list_trig_obs exists
                    if pos.rep > self.list_trig_obs[-1] :                         # the pos.rep is > to the trig value of the observed pos
                        self.track_and_fluo_add_trig_nb_rep(pos)                  # make reptrig for this position : prepare the trig
                else:
                    self.track_and_fluo_add_trig_nb_rep(pos)                      # if trig list is empty.. add this trig event

    def track_and_fluo_trig_rfp(self, pos, SC, debug=[0,1]):
        '''
        Follow mitosis,
        Trigger the RFP and increase the frequency
        '''
        print(f'### pos.tracking {pos.tracking}, pos.rep {pos.rep},  pos.reptrig {pos.reptrig} ')
        # try:
        if pos.tracking and (pos.rep == pos.reptrig):                        # triggering fluo near mitosis
            self.trig_obs_time = time()                                        # time of obs beginning
            print('Time of observation reinitialized..')
            print('higher frequency of observation !!!')
            pos.list_steps['fluo_rfp'] = STEP(val=SC, kind='fluo', attr={'kind_fluo' : 'rfp'})        # adding RFP after BF
            if 0 in debug: print('Inserted fluorescence in the pos list_steps actions')
            if 1 in debug:
                for i,step in enumerate(pos.list_steps):
                    print(f'num step is {i}')
                    try:
                        print(f'#### step.kind is {step.kind}')
                    except:
                        print('step is probably None and has no kind attribute')
        # except:
        #     print('no pos.reptrig yet !!!')
        try:
            print(f'Will trigger RFP in {(pos.reptrig - pos.rep)*self.delay} min')
        except:
            print('pos.reptrig  probably not existing yet..')

    def track_and_fluo_mess0(self, pos, debug=[1]):
        '''
        Follow mitosis,
        '''
        print('-------------------------------------')
        print(Fore.BLUE + f'Dealing with position n° {pos.num}')
        print(Style.RESET_ALL)
        try:
            if 1 in debug : print(f'pos.list_budding_cells is {pos.list_budding_cells} ')
        except:
            pass

    def rand_list(self,ll):
        '''
        shuffle list
        '''
        return random.sample(ll, len(ll))
