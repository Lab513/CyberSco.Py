from time import sleep
from datetime import datetime
from flask_socketio import emit
from modules.util_misc import *
import tqdm
import shutil as sh
import oyaml as yaml
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

from modules.modules_mda.monitor_mda import MONITORING as MON

class PREDEF_MDA(MON):
    '''
    '''

    def __init__(self, server=None):
        '''
        '''
        self.server = server

    # At beginning

    def init_files_save_infos_etc(self):
        '''
        Saving both the experiment informations and the protocole.
        '''
        # save the experiment infos (author, microscope etc..)
        self.save_experim_infos()
        self.save_protocol()        # save the protocol in the mda folder

    # During mda

    def delay_sleep(self):
        '''
        Delay until next repetition
        '''
        now1 = datetime.now()
        dt_meas = (now1 - self.now0).seconds
        # delay time in second after extracting time elapsed
        dt = int(self.delay*60 - dt_meas)
        print(f'time for measurements is {dt_meas} s')
        print(f'time dt before repeating measurements is {dt} s')
        # progressbar for the time left until next measurements
        for _ in tqdm.tqdm(range(dt)):
            # progressbar step 1 second
            sleep(1)

    # Time axis for figures

    def save_time_axis(self):
        '''
        Save the times for each frame in a yaml file
        '''
        for pos in self.list_pos:
            addr_time_axis_pos = opj(self.dir_mda_temp,
                                     f'time_axis_pos{pos.num}.yaml')
            with open(addr_time_axis_pos, "w") as f_w:
                yaml.dump(pos.list_time_axis, f_w)

    def take_elapsed_time(self):
        '''
        Time elapsed since self.first_time
        '''
        self.now0 = datetime.now()
        self.deltat = (self.now0 - self.first_time).seconds
        tmin = round(self.deltat/60, 1)
        # time elapse from beginning
        print(f'######### time elapsed from the beginning is {tmin} min')
        self.server.sleep(0.1)
        # send index of current repetition
        emit('time_elapsed', str(tmin))
        print('sent time elapsed')

    def start_time(self):
        '''
        origin of the time
        '''
        self.first_time = datetime.now()

    def current_time(self):
        '''
        find current time in minutes
        '''
        self.curr_time =  int((datetime.now() - self.first_time).seconds/60)

    def trig_per_event(self, phase):
        '''
        Trigger periodic event
        True when the phase is in the range of period +/- delay/2
        '''
        return ((self.curr_time + phase) % self.per_pulse) < self.delay

    def actions_after_check_conditions(self,rep):
        '''
        '''
        self.plot_nbcells_positions(rep)         # plot the number of cells
        self.save_nb_rep(rep)
        self.save_time_axis()                    # save the time axis
        if self.monitor_params:
            # following messages during mda, monitoring etc..
            self.messages_after_measurement(rep)
        self.make_video_positions(rep)         # video of each position
        self.server.sleep(0.1)
        # send index of current repetition
        emit('curr_rep', str(rep))

    # end of predef

    def save_experim(self):
        '''
        Copy mda_temp in mda_experiments with a date at the end
        '''
        name_mda_folder = opb(self.dir_mda_temp)
        target_dir = opj(os.getcwd(), 'mda_experiments',
                         name_mda_folder + '_' + self.date())
        sh.copytree(self.dir_mda_temp, target_dir)

    def close_devices(self):
        '''
        Close serial port on the devices
        '''
        for dev in self.ldevices:
            cl_name = dev.__class__.__name__
            try:
                dev.close()
                print(f'closed {cl_name}')
            except:
                print(f'cannot close {cl_name}')

    ##########  Predefined MDA protocol..

    def launch_loop(self):
        '''
        launch_loop for the MDA experiment
         in the case of PREDEFINED experiments
        '''
        self.first_time = datetime.now()
        self.init_files_save_infos_etc()
        self.init_conditions()                # initial conditions for the mda
        self.init_nb_pos(len(self.list_pos))
        for rep in range(self.repeat):        # Loop
            self.mess_num_measurement(rep)
            self.take_elapsed_time()
            for ind_pos, pos in enumerate(self.list_pos):
                # make all the steps in this position
                pos.make_steps(rep,ind_pos)
                sleep(0.1)
            self.check_conditions(rep)           # apply the conditions
            self.actions_after_check_conditions(rep)
            if rep < self.repeat-1:
                # respect delay between each beginning of measurement
                self.delay_sleep()
            # duplicate mda_temp for monitoring..
            self.copy_monitor(self.dir_mda_temp, self.dir_mda_temp_dash)
        # save the MDA with the date at the end of the MDA
        # self.save_experim()
        # close the serial port of all the devices
        self.close_devices()
