'''
Mda experiments
'''

from time import sleep
from datetime import datetime
from matplotlib import pyplot as plt
from pathlib import Path
from colorama import Fore, Style
from flask_socketio import emit
import shutil as sh
import oyaml as yaml
import tqdm
from modules.util import Logger
from modules.util_server import find_platform, chose_server
from modules.util_misc import *

from modules.modules_mda.mail import GMAIL
from modules.modules_mda.mail_attachments import MAIL_ATTACH as MA
from modules.modules_mda.plot_bokeh import BOKEH_PLOT
from modules.modules_mda.positions import POS
from modules.modules_mda.mda_tree_protocol import MDA_TREE_PROTOCOL as MTP
from modules.modules_mda.make_all_videos_for_position\
            import MAKE_VIDEOS_POSITION as MVP
from tensorflow.keras import models
import sys
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

platf = find_platform()
server = chose_server(platf)


class EVENT():
    '''
    Event
    '''
    def __init__(self, name=None):
        '''
        Object event
        '''
        self.name = name  # kind of action
        self.happened = False
        self.exists = False


class STEP():
    '''
    Step
    '''
    def __init__(self, val, kind, attr=None):
        '''
        Unit of action
        '''
        self.kind = kind     # kind of action
        self.val = val       # value for the action
        if attr:
            for k, v in attr.items():
                setattr(self, k, v)


class MDA(POS, MA, MVP, MTP):
    '''
    Mda experiment
    '''
    def __init__(self, ldevices=None, title=''):
        '''
        ldevices : camera, gates, microscope, stage, fluorescence lights
        '''
        MTP.__init__(self)
        self.list_pos = []                # list of positions
        self.lpos_id = []              # list of the ids for the positions
        self.lxyz = []                    # list for predefined pos
        self.loffsets = []                # list of the offsets for ZDC
        self.list_gates = []              # list of the gates
        self.list_SC_ET = []     # list for settings channel and exposure time
        self.list_AF = []                 # of the kind of autofocuses
        self.ldevices = ldevices          # list of the devices
        self.folder_exp()                 # folder for experiment
        self.logfile()                    # save stdout in logfile
        self.load_main_model()            # load current model
        self.load_event_model()           # load event model
        self.gates_blocked = []
        self.gates_switched = []
        self.load_addr_mails()            # load the mails addresses
        self.ga = self.ldevices[-1]       # object gate in mda
        self.co = ldevices[3]             # Cooled
        self.event = EVENT()
        self.cond = None
        # self.freq_messages = 20      # number of minutes between each message
        self.list_trig_obs = []
        self.list = []
        self.title = title
        self.kind_focus = 'afml_sweep'       # type of focus used

    def load_main_model(self):
        '''
        '''
        with open('modules/settings/model_obj.yaml') as f_r:
            obj = self.ldevices[0].objective
            curr_mod = yaml.load(f_r, Loader=yaml.FullLoader)[obj]
            self.curr_mod = self.load_model(curr_mod)        # main model

    def load_event_model(self):
        '''
        Load the model for event detection
        '''
        with open('modules/settings/event_model.yaml') as f_r:
            ev_mod = yaml.load(f_r, Loader=yaml.FullLoader)
            self.ev_mod = self.load_model(ev_mod)              # event model

    def load_addr_mails(self):
        '''
        Mail for sending information during the experiment
        '''
        self.gm = GMAIL()
        try:
            with open('interface/settings/mail_addresses.yaml') as f_r:
                self.dic_dest = yaml.load(f_r, Loader=yaml.FullLoader)
        except:
            self.dic_dest = {}
            print('mail_addresses.yaml not found !!!')

    def send_to(self, *lnames):
        '''
        send_to(name) or send_to('all')
        '''
        lnames = list(lnames)
        if lnames[0] == 'all':
            sent_addr_mail = []
            for v in self.dic_dest.values():
                sent_addr_mail += [v]
        else:
            sent_addr_mail = []
            for name in lnames:
                sent_addr_mail += [self.dic_dest[name]]
        print(f'sent_addr_mail is {sent_addr_mail}')
        return sent_addr_mail

    def load_model(self, mod):
        '''
        Loading the models
        ep5_v3 : segmentation model for 40x
        ep15_x20_otsu : segmentation model for 20x
        '''
        with open('modules/settings/models.yaml') as f_r:
            dic_mod = yaml.load(f_r, Loader=yaml.FullLoader)
        model_loaded = models.load_model(Path('models') / dic_mod[mod])
        return model_loaded

    @property
    def date(self):
        '''
        Return a string with day, month, year, Hour and Minute..
        '''
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M")
        return dt_string

    def logfile(self):
        '''
        Log file with standard err and output
        '''
        sys.stdout = Logger()

    def folder_exp(self):           # folder experiment
        '''
        Handle the temporary mda folder
        '''
        self.dir_mda_temp = opj(os.getcwd(), 'mda_temp')      # mda folder
        self.dir_test = opj(os.getcwd(), 'test')          # test folder
        # folder for init params of the predefined mda
        mda_init = opj(self.dir_mda_temp, 'mda_init')
        # folder for producing video
        imgs_videos = opj(self.dir_mda_temp, 'imgs_for_videos')
        # folder for producing BF-RFP video
        imgs_BF_fluo_videos = opj(self.dir_mda_temp, 'imgs_for_BF_RFP_videos')
        # folder for producing GFP video
        imgs_GFP_videos = opj(self.dir_mda_temp, 'imgs_for_GFP_videos')
        # folder for the monitorings
        monitorings = opj(self.dir_mda_temp, 'monitorings')
        # folder for predictions
        pred = opj(self.dir_mda_temp, 'monitorings', 'pred')
        # folder for contours
        cntrs = opj(self.dir_mda_temp, 'monitorings', 'cntrs')
        # folder for nb_cells
        nb_cells = opj(self.dir_mda_temp, 'monitorings', 'nb_cells')
        # folder for the tracking
        tracking = opj(self.dir_mda_temp, 'monitorings', 'tracking')
        # folder for superp_cntrs
        superp_cntrs = opj(self.dir_mda_temp, 'monitorings', 'superp_cntrs')
        # folder for events
        events = opj(self.dir_mda_temp, 'monitorings', 'events')
        # folder for autofocus
        AF = opj(self.dir_mda_temp, 'monitorings', 'AF')
        # folder for autofocus ML images
        AF_ML = opj(self.dir_mda_temp, 'monitorings', 'AF', 'ML')
        # folder for autofocus Laplacian images
        AF_Lap = opj(self.dir_mda_temp, 'monitorings', 'AF', 'Lap')
        # folder for current experiment
        experim = opj(self.dir_mda_temp, 'monitorings', 'experim')
        # folder for autofocus with ML method
        imgs_for_AF_ML = opj(self.dir_mda_temp, 'monitorings',
                             'AF', 'imgs_for_AF_ML')
        # folder for autofocus with ML method
        imgs_for_AF_ML_direct_training = opj(self.dir_mda_temp,
                                             'monitorings', 'AF',
                                             'imgs_for_AF_ML_direct_training')
        movie = opj(self.dir_test, 'movie')
        try:
            #sys.stdout.close()
            print(f'trying to remove {self.dir_mda_temp} ')
            sh.rmtree(self.dir_mda_temp)
        except:
            print('no mda folder')
        try:
            sh.rmtree(self.dir_test)
        except:
            print('no test folder')
        os.makedirs(self.dir_mda_temp)          # mda folder
        os.makedirs(imgs_videos)
        os.makedirs(mda_init)
        os.makedirs(imgs_BF_fluo_videos)
        os.makedirs(imgs_GFP_videos)
        os.makedirs(monitorings)
        os.makedirs(pred)
        os.makedirs(cntrs)
        os.makedirs(nb_cells)
        os.makedirs(tracking)
        os.makedirs(superp_cntrs)
        os.makedirs(events)
        os.makedirs(AF)
        os.makedirs(AF_ML)
        os.makedirs(AF_Lap)
        os.makedirs(experim)
        os.makedirs(imgs_for_AF_ML)
        os.makedirs(imgs_for_AF_ML_direct_training)
        os.makedirs(movie)

    def init_positions(self):
        '''
        Create the positions from the interface informations
        '''
        self.nb_pos = len(self.lxyz)
        for i in range(self.nb_pos):
            pos = POS(self.ldevices, self.curr_mod, self.ev_mod)
            pos.num = i
            pos.dir_mda_temp = self.dir_mda_temp
            pos.mda = self
            # list of the positions in the mda object
            self.list_pos += [pos]
            # retrieve the coordinate of each position..
            pos.init_xyz = self.lxyz[i]
            pos.list_steps = {'posxyz': None, 'refocus': None,
                              'take_pic': None, 'fluo_rfp': None,
                              'fluo_gfp': None}

    def get_positions(self, debug=[0]):
        '''
        Load the positions
        lxyz : list of positions [[x0,y0,z0], [x1,y1,z1]..]
        '''
        self.init_positions()
        for i, xyz in enumerate(self.lxyz):
            print(f'i: {i}')
            print(f'xyz: {xyz}')
            # ref_posz for the AF
            self.list_pos[i].ref_posz = xyz[2]
            # xy = [posx,posy]
            self.list_pos[i].list_steps['posxyz'] = STEP(xyz, kind='posxyz')
            if 0 in debug:
                print(f'In mda.get_positions,\
                      self.list_pos[i].ol.ref_posz'
                      f' = {self.list_pos[i].ref_posz} ')

    def prepare_channels(self, dic_chan_set):
        '''
        Apply the Cooled "settings channels" from the interface values
        '''
        self.co.prepare_channels(dic_chan_set['COOL'])

    def get_chan_set(self):
        '''
        Load dic_chan_set for the channels settings
        '''
        print(f'#### self.list_SC_ET is {self.list_SC_ET}')
        for i, pos in enumerate(self.list_pos):
            try:
                # load chan set for each pos
                pos.chan_set = self.list_SC_ET[i]
            except:
                pos.chan_set = None

    def get_gates(self):
        '''
        Load the gate Id for each position
        '''
        print(f'#### self.list_gates is {self.list_gates}')
        for i, pos in enumerate(self.list_pos):
            try:
                # give a value to attribute gate
                pos.num_gate = int(self.list_gates[i])
            except:
                pos.num_gate = None

    def get_kind_focus(self):
        '''
        Retrieve the kind of focus
        '''
        for i, pos in enumerate(self.list_pos):
            # attach focus method to position
            pos.ol.kind_focus = self.list_AF[i]
            print(f'pos.ol.kind_focus is {pos.ol.kind_focus}')
            # attach the kind of AFML to the position
            pos.ol.afml_optim = self.afml_optim

    def refocus(self, all=True, debug=[0]):
        '''
        Refocus on the first position
        '''
        if 0 in debug:
            print(f'len(self.list_pos) = {len(self.list_pos)} ')
        if all:
            for pos in self.list_pos:
                pos.list_steps['refocus'] = STEP(None, kind='refocus')
        else:
            self.list_pos[0].list_steps['refocus'] = STEP(None, kind='refocus')

    def take_pic(self, debug=[0]):
        '''
        Take a picture in BF
        '''
        for pos in self.list_pos:
            pos.list_steps['take_pic'] = STEP(val=pos.chan_set, kind='cam')
            if 0 in debug:
                print(f'pos.list_steps.keys() = {pos.list_steps.keys()}')

    def take_pic_fluo(self, kind_fluo,
                      mask=None,
                      mask_exp_time=None):
        '''
        Take a picture in fluorescence
        pos.chan_set : list with dictionary
                       containing the name and exp time
                       of the SC
        '''
        for pos in self.list_pos:
            pos.list_steps[f'fluo_{kind_fluo}'] =\
                STEP(val=pos.chan_set, kind='fluo',
                     attr={'kind_fluo': kind_fluo,
                           'mask': mask,
                           'mask_exp_time': mask_exp_time})

    def analyse_pic(self):
        '''
        Analyse the resulting image
        '''
        for pos in self.list_pos:
            # analysis when at last image
            pos.list_steps['cells_analysis'] =\
             STEP(None, kind='cells_analysis')

    def save_experim(self):
        '''
        Copy mda_temp in mda_experiments with a date
        '''
        name_mda_folder = opb(self.dir_mda_temp)
        target_dir = opj(os.getcwd(), 'mda_experiments',
                         name_mda_folder + '_' + self.date)
        sh.copytree(self.dir_mda_temp, target_dir)

    ## During mda

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

    def plot_nbcells_until_rep(self, rep):
        '''
        Evolution of nb of cells
        '''
        plt.figure()
        plt.title(f"#cells until rep {rep}")
        plt.xlabel('time in min')
        plt.ylabel('nb of cells')
        for pos in self.list_pos:
            plt.ylim(0, max(pos.list_nb_cells)*1.3)
            plt.locator_params(nbins=5)
            plt.plot(pos.list_time_axis, pos.list_nb_cells, label=str(pos.num))
        addr_plot_comp = opj(self.folder_nbcells, f'nbcells_until_last.png')
        plt.legend()
        plt.savefig(addr_plot_comp)

    def plot_nbcells_positions(self, rep):
        '''
        Compare nb of cells between the positions
        '''
        self.folder_nbcells = opj(self.dir_mda_temp, 'monitorings', 'nb_cells')
        # save the list of nb cells in yaml file after each acquisition
        self.save_nbcells_positions()
        try:
            self.plot_nbcells_until_rep(rep)
        except:
            print('###### Cannot plot the nb'
                  ' of cells with plot_nbcells_until_rep ')
        try:
            self.last_bokeh_plot_nbcells(rep)
        except:
            print('Tried to plot bokeh')

    def last_bokeh_plot_nbcells(self, rep, debug=[]):
        '''
        Plot Bokeh of the nb of cells in the various positions
        '''
        try:
            os.remove(self.addr_bokeh_nbcells)
        except:
            print('trying os.remove(self.addr_bokeh_nbcells)')
        bk = BOKEH_PLOT()
        bk.title("Evolution of the number of cells")
        bk.xlabel('time in min')
        bk.ylabel('nb of cells')
        for pos in self.list_pos:
            if 1 in debug:
                print(f'pos.list_nb_cells is {pos.list_nb_cells} ')
            bk.plot(pos.list_time_axis, pos.list_nb_cells, label=str(pos.num))
        self.addr_bokeh_nbcells = opj(self.folder_nbcells, f'nbcells.html')
        bk.legend()
        bk.show()
        bk.savefig(self.addr_bokeh_nbcells)

    def save_nbcells_positions(self):
        '''
        Save nb of cells for each position in a yaml file
        '''
        for pos in self.list_pos:
            addr_nb_cells_pos = opj(self.folder_nbcells,
                                    f'list_nb_cells_pos{pos.num}.yaml')
            with open(addr_nb_cells_pos, "w") as f_w:
                yaml.dump(pos.list_nb_cells, f_w)

    def save_time_axis(self):
        '''
        Save the times for each frame in a yaml file
        '''
        for pos in self.list_pos:
            addr_time_axis_pos = opj(self.dir_mda_temp,
                                     f'time_axis_pos{pos.num}.yaml')
            with open(addr_time_axis_pos, "w") as f_w:
                yaml.dump(pos.list_time_axis, f_w)

    def sending_mess_with_gmail(self, to, attach):
        '''
        Sending nb cell evolution by gmail..
        '''
        self.gm.send(to=to,
                     subject='experiment',
                     text="hello",
                     attach=attach
                     )
        print('sent message with gmail')

    def attach_pieces_to_mail(self, pos, rep):
        '''
        Attaching documents to the mail
        '''
        # attach the last image of the position
        self.attach_BF_image(pos, rep)
        # attach the video of the position
        self.attach_BF_video(pos)
        # attach the curve used for AF with ML
        self.attach_ML_focus_curve(pos, rep)
        # attach the video of tracking
        self.attach_tracking_video(pos)
        # attach the video of superposition
        self.attach_superp_video(pos)
        # attach the video of AF ML
        self.attach_AF_ML_video(pos)
        # attach the video of AF Lap
        self.attach_AF_Lap_video(pos)
        # attach the Bokeh file for pos z
        self.attach_AF_list_posz(pos)
        # attach superposition of BF and RFP
        self.attach_bf_rfp_video(pos)
        # attach superposition of GFP
        self.attach_gfp_video(pos)
        # attach superposition of BF, RFP and buds
        self.attach_bf_rfp_buds_video(pos)
        # attach the infos about the experiment
        self.attach_experim_infos()
        # attach the events
        self.attach_events_images(pos)
        # attach the log file
        #self.attach_log_file()

    def monitoring_with_mail(self, rep, debug=[]):
        '''
        Send messages and attached pieces
        '''
        self.attach = []
        curr_time = round(self.deltat/60, 1)
        print(f"self.monitor_params['delay_messages']"
              " {self.monitor_params['delay_messages']} min")
        # sending message every self.monitor_params['delay_messages'] minutes
        if curr_time % int(self.monitor_params['delay_messages']) < self.delay:
            to = self.send_to('Lionel')
            #attach = opj(self.dir_mda_temp, f'nbcells_until_rep{rep}.png') # addr plot nb cells curves
            if os.path.exists(self.addr_bokeh_nbcells):
                self.attach += [self.addr_bokeh_nbcells]
            for pos in self.list_pos:
                self.attach_pieces_to_mail(pos, rep)
            if 1 in debug:
                print(f'attach is {self.attach} ')
            try:
                # sending to dest with attached
                self.sending_mess_with_gmail(to, self.attach)
            except:
                print('Cannot send mail..')

    def messages_after_measurement(self, rep, debug=[]):
        '''
        Messages, mails and alerts
        '''
        print(Fore.YELLOW + f'end of measurement num {int(rep) + 1}')
        print(Style.RESET_ALL)
        print(f'waiting {self.delay} min...')
        # monitor the mda via mail
        if self.monitor_params['mail']:
            self.monitoring_with_mail(rep)

    def take_elapsed_time(self):
        '''
        Time elapsed since self.first_time
        '''
        self.now0 = datetime.now()
        self.deltat = (self.now0 - self.first_time).seconds
        tmin = round(self.deltat/60, 1)
        # time elapse from beginning
        print(f'######### time elapsed from the beginning is {tmin} min')
        server.sleep(0.1)
        # send index of current repetition
        emit('time_elapsed', str(tmin))
        print('sent time elapsed')

    def actions_after_check_conditions(self,rep):
        '''
        '''
        self.plot_nbcells_positions(rep)         # plot the number of cells
        self.save_time_axis()                    # save the time axis
        if self.monitor_params:
            # following messages during mda, monitoring etc..
            self.messages_after_measurement(rep)
        self.make_video_positions(rep)         # video of each position
        server.sleep(0.1)
        # send index of current repetition
        emit('curr_rep', str(rep))

    def mess_num_measurement(self, rep):
        '''
        Indicate the beginning of the measurement
        '''
        print('#############################################################')
        print('***')
        print(Fore.YELLOW + f'measurement num {int(rep) + 1}...')
        print(Style.RESET_ALL)
        print('***')
        print('#############################################################')

    def init_files_save_infos_etc(self):
        '''
        '''
        # save the experiment infos (author, miroscope etc..)
        self.save_experim_infos()
        self.save_protocol()        # save the protocol in the mda folder

    def launch_loop(self):
        '''
        launch_loop for the MDA experiment
         in the case of predefined experiments
        '''
        self.first_time = datetime.now()
        self.init_files_save_infos_etc()
        self.init_conditions()                # initial conditions for the mda
        for rep in range(self.repeat):        # Loop
            self.mess_num_measurement(rep)
            self.take_elapsed_time()
            for pos in self.list_pos:
                # make all the steps in this position
                pos.make_steps(rep)
                sleep(0.1)
            self.check_conditions(rep)           # apply the conditions
            self.actions_after_check_conditions(rep)
            if rep < self.repeat-1:
                # respect delay between each beginning of measurement
                self.delay_sleep()
        # save the MDA with the date at the end of the MDA
        self.save_experim()
        # close the serial port of all the devices
        self.close_devices()

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

    def loop(self, debug=[0]):
        '''
        MDA loop
        '''
        # save the informations about the experiment
        self.save_experim_infos()
        print(f'Current protocol is  : {self.title} ')
        # launching the main loop
        if 0 in debug:
            print(f'In mda.py, self.list is {self.list}')
        self.list[0].loop()

    def save_experim_infos(self):
        '''
        Copy the information about the experiment with the mda results
        '''
        # infos about the experiment
        infos = opj('interface', 'infos_mda', 'experiment_infos.yaml')
        sh.copy(infos, self.dir_mda_temp)

    def save_protocol(self):
        '''
        Copy the protocol in the mda folder
        '''
        # protocol used for the experiment
        prot = opj('interface', 'static', 'mda_protocols', self.curr_prot)
        sh.copy(prot, self.dir_mda_temp)
