from time import sleep, time
from modules.modules_mda.monitor_mda import MONITORING as MON
# Color in the Terminal
from colorama import Fore, Style
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename


class LOOP(MON):
    '''
    Loop over positions
    '''

    def __init__(self, nb_rep, time_rep):
        '''
        nb_rep : number of repetions of the loop
        time_rep : time between repetitions in the loop (in minutes)
        '''
        self.list = []                         # list of elements over which to loop
        self.nb_rep = int(nb_rep)              # number of repetitions
        self.time_rep = float(time_rep)        # repetition time

    def handle_delay(self,t0,t00,rep):
        '''
        Calculate and apply the delay before the next repetition.
        '''
        # delay between the iterations in minutes
        t1 = time()
        t_tot = round(t1-t00,1)
        print(f'##### time from the beginning is {t_tot} s #####')
        t_meas = round(t1-t0,2)
        print(f'time for the current turn: {t_meas} sec')

        # removing measurement time from repetition delay..
        tsleep = round(self.time_rep*60-t_meas,1)
        if rep != self.nb_rep-1:
            print(f'time before next repetition is {tsleep} sec')
        sleep(tsleep)

    def indicate_curr_iter(self,rep):
        '''
        Show the current iteration index..
        '''
        print(Fore.YELLOW + f'\n iteration num {rep}')
        print(Style.RESET_ALL)

    def indicate_loop_params(self):
        '''
        Indicate the nb of repetitions and the delay time..
        '''
        print(Fore.GREEN + f'\n### nb_rep {self.nb_rep}, '
              f' time per repetition {self.time_rep} min ')
        print(Style.RESET_ALL)

    def save_nb_rep(self, rep):
        '''
        Save the number of repetitions in monitorings..
        '''
        with open(opj('mda_temp', 'monitorings', 'nb_rep.txt'),'w') as fw:
            fw.write(str(rep))

    def loop(self, src_addr, dest_addr, monitor_params, event, debug=[]):
        '''
        Execute the MDA loop
        '''
        self.dir_mda_temp = src_addr
        self.list_pos = self.list
        t00 = time()
        self.indicate_loop_params()
        self.monitor_params = monitor_params
        self.delay = self.time_rep
        for rep in range(self.nb_rep):
            self.indicate_curr_iter(rep)
            t0 = time()
            for elem in self.list:
                elem.loop(rep, event)                   # trigger the loop of elem
            if 1 in debug:
                print(f'In loop, dest_addr is { dest_addr }')
            self.actions_after_check_conditions(rep)
            self.copy_monitor(src_addr, dest_addr)
            self.handle_delay(t0,t00,rep)
            self.save_nb_rep(rep)

        print(Fore.YELLOW + f'\n            ##### END of the MDA #####')
        print(Style.RESET_ALL)
