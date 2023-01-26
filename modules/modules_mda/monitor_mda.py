from time import time
from modules.modules_mda.mail import GMAIL
from matplotlib import pyplot as plt
from modules.modules_mda.mail_attachments import MAIL_ATTACH as MA
from modules.modules_mda.make_all_videos_for_position\
                                       import MAKE_VIDEOS_POSITION as MVP
from modules.modules_mda.plot_bokeh import BOKEH_PLOT
from colorama import Fore, Style
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename
import shutil as sh
import oyaml as yaml


class MONITORING(MVP):
    '''
    MDA monitoring..
    '''

    def __init__(self):
        '''
        '''
        # Authorized pattern for copying to the dashboard changing files
        self.list_patt_auth = ['nbcells_segm']

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
        # self.sensors_info()

    def save_nb_rep(self, rep):
        '''
        Save the number of repetitions in monitorings..
        '''
        with open(opj(self.dir_mda_temp, 'monitorings', 'nb_rep.txt'),'w') as fw:
            fw.write(str(rep))

    def init_count_rep(self):
        '''
        file to register the current repetition index
        '''
        with open(opj(self.dir_mda_temp, 'monitorings', 'nb_rep.txt'), "w") as fw:
            fw.write('0')

    def init_pic_time(self):
        '''
        yaml file containing information about repetitions and time of the positions..
        '''
        with open(opj(self.dir_mda_temp, 'monitorings', 'pic_time.yaml'), "w") as fw:
            yaml.dump({'0':{'0':'0'}}, fw)

    def init_info_sensors(self):
        '''
        yaml file containing the sensors information..
        '''
        with open(opj(self.dir_mda_temp, 'monitorings', 'sensors.yaml'), "w") as fw:
            yaml.dump({'0':{'light':'0', 'temp':'0'}}, fw)

    def init_nb_pos(self, nb_pos):
        '''
        file for the number of positions
        '''
        with open(opj(self.dir_mda_temp, 'monitorings', 'nb_pos.txt'), "w") as fw:
            fw.write(str(nb_pos))

    # Mails

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
              f" {self.monitor_params['delay_messages']} min")
        # sending message every self.monitor_params['delay_messages'] minutes
        if curr_time % int(self.monitor_params['delay_messages']) < self.delay:
            to = self.send_to('Lionel')
            #attach = opj(self.dir_mda_temp, f'nbcells_until_rep{rep}.png') # addr plot nb cells curves
            if os.path.exists(self.addr_bokeh_nbcells_segm0):
                self.attach += [self.addr_bokeh_nbcells_segm0]
            for pos in self.list_pos:
                self.attach_pieces_to_mail(pos, rep)
            if 1 in debug:
                print(f'attach is {self.attach} ')
            try:
                # sending to dest with attached
                self.sending_mess_with_gmail(to, self.attach)
            except:
                print('Cannot send mail..')

    # Number of cells

    def plot_nbcells_until_rep(self, rep):
        '''
        Evolution of nb of cells Mpl plot
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

    def find_max_bk_plot(self, pos, max_plot, num_mod):
        '''
        '''
        if num_mod == 0:
            max_pos = max(pos.list_nb_cells)
            if max_pos > max_plot:
                max_plot = max_pos
        else:
            max_pos = max(pos.list_nb_cells_events)
            if max_pos > max_plot:
                max_plot = max_pos

        return max_plot

    def bokeh_plot_nbcells_segm(self, num_mod, w=300, h=240 , debug=[]):
        '''
        Bokeh plot for the cells segmented with model num_mod
        Gathering the positions on the same graph..
        num_mod : index of the model
        '''
        bk = BOKEH_PLOT(plot_width=w, plot_height=h)
        # bk.figure()
        p0 = self.list_pos[0]
        name_mod = p0.used_models[f'mod{num_mod}']['name']
        bk.title(f"Number of cells, model {name_mod}")
        bk.xlabel('time in min')
        bk.ylabel('nb of cells')
        max_plot = 0
        for pos in self.list_pos:
            if 1 in debug:
                print(f'pos.list_nb_cells is {pos.list_nb_cells} ')
                print(f'pos.list_nb_cells_events is {pos.list_nb_cells_events} ')
                print(f'pos.list_time_axis is  {pos.list_time_axis}')
                print(f'pos.num is  {pos.num}')
            max_plot = self.find_max_bk_plot(pos, max_plot, num_mod)
            if num_mod == 0:
                bk.plot(pos.list_time_axis, pos.list_nb_cells, label=str(pos.num))
            else:
                bk.plot(pos.list_time_axis, pos.list_nb_cells_events, label=str(pos.num))
        bk.ylim(0,max_plot*1.3)
        addr = opj(self.folder_nbcells, f'nbcells_segm{num_mod}.html')
        setattr(self, f'addr_bokeh_nbcells_segm{num_mod}', addr)
        bk.legend()
        bk.show()
        bk.savefig(addr)

    def clean_bokehs(self):
        '''
        Clean the Bokeh plots of the nb of cells
        '''
        for ind in [0,1]:
            try:
                name_bokeh = f'addr_bokeh_nbcells_segm{ind}'
                os.remove(getattr(self, name_bokeh))
            except:
                print(f'trying to remove {name_bokeh}')
        try:
            os.remove(self.addr_bokeh_nbcells_segm1)
        except:
            print('trying os.remove(self.addr_bokeh_nbcells_segm1)')

    def last_bokeh_plot_nbcells(self, rep, debug=[]):
        '''
        Plot Bokeh of the nb of cells in the various positions
        '''
        self.clean_bokehs()
        # bokeh nb cells model 0
        self.bokeh_plot_nbcells_segm(0)
        # bokeh nb cells model 1
        self.bokeh_plot_nbcells_segm(1)

    def save_nbcells_positions(self):
        '''
        Save nb of cells for each position in a yaml file
        '''
        for pos in self.list_pos:
            addr_nb_cells_pos = opj(self.folder_nbcells,
                                    f'list_nb_cells_segm0_pos{pos.num}.yaml')
            with open(addr_nb_cells_pos, "w") as f_w:
                yaml.dump(pos.list_nb_cells, f_w)

            addr_nb_cells_pos = opj(self.folder_nbcells,
                                    f'list_nb_cells_segm1_pos{pos.num}.yaml')
            with open(addr_nb_cells_pos, "w") as f_w:
                yaml.dump(pos.list_nb_cells, f_w)

    def test_file_in_patt(self,f):
        '''
        Find if pattern is in the name of file..
        '''
        auth = False
        for patt in self.list_patt_auth:
            if patt in f:
                auth = True

        return auth

    def copy_monitor(self, root_src_dir, dest_addr, debug=[0]):
        '''
        Copy the MDA in the Dashboard for monitoring at distance..
        '''
        # try:
        # root_src_dir = opj(os.getcwd(), 'mda_temp')
        if 0 in debug:
            print(f'root_src_dir is {root_src_dir}')
            print(f'dest_addr is {dest_addr}')
        t0 = time()
        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, dest_addr, 1)
            if not op.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = opj(src_dir, file_)
                dst_file = opj(dst_dir, file_)
                test_patt = self.test_file_in_patt(file_)
                if not op.exists(dst_file) or test_patt:
                    sh.copy(src_file, dst_dir)
        t1 = time()
        print(f'time for copying is {round((t1-t0)/60,2)} min')
        # except:
        #     print('Cannot copy the new acquisiton to the Dashboard folder.. ')

    def actions_after_check_conditions(self,rep):
        '''
        Save the monitorings after each repetition..
        '''
        # try:
        self.plot_nbcells_positions(rep)         # plot the number of cells
        # except:
        #     print('Cannot plot the nb of cells.. ')
        self.save_nb_rep(rep)
        self.save_time_axis()                    # save the time axis
        if self.monitor_params:
            # following messages during mda, monitoring etc..
            self.messages_after_measurement(rep)
        self.make_video_positions(rep)         # video of each position

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
