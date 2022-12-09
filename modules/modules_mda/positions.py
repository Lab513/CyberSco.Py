from time import sleep
from datetime import datetime
from collections import defaultdict, OrderedDict
import oyaml as yaml
import numpy as np
from colorama import Fore, Style

from flask_socketio import emit
import subprocess
import cv2
from modules.util_server import find_platform, chose_server
from modules.util_misc import *
import time
import shutil as sh

import interface.modules.init.init_glob_vars as g
from modules.modules_mda.make_video import MAKE_VIDEO as MV
from modules.track_segm.cam_pred import CAM_PRED as CP
from modules.modules_mda.tracking import TRACK as TR
from modules.predef.plugins.plugins_funcs.hog1_curves import HOG1 as HG
from interface.modules.DMD.calib import apply_calib

import re
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

platf = find_platform()
server = chose_server(platf)

ts_sleep = 0.05


class POS(MV, CP, TR, HG):
    '''
    Position on which are made the autofocus, BF, RFP, YFP etc...
    '''
    def __init__(self, ldevices, mod0=None, mod1=None, title='', debug=[0]):
        '''
        Position
        '''
        lcls = [MV, CP, TR, HG]
        [cl.__init__(self) for cl in lcls]
        self.ldevices = ldevices
        # load the devices
        self.ol, self.pr, self.ev, self.co, self.xc, self.ga, self.se = ldevices
        self.mod0 = mod0                   # current segmentation model
        self.mod1 = mod1                       # current event model
        self.retrieve_models_infos()
        self.list_steps = OrderedDict()
        self.size = 512                            # images size
        self.nb_cells = 0                          # current number of cells
        # list of the nb of cells during the experiment
        self.list_nb_cells = []
        self.dic_fluo = {'rfp': {'ch': 'C', 'filt': 5},
                         'gfp': {'ch': 'B', 'filt': 3}}
        self.blocked = False           # by default the position is not blocked
        self.switched = False
        self.tracking = False
        # tracking
        self.track_in_analysis = False           # by default, no tracking
        self.segm_all_buds = False
        self.all_cntrs = {}
        self.all_cntrs_fluo = {}
        self.track_method = 2                    # method used for tracking
        self.show_num_cell = True
        self.erode_after_pred = False
        self.which_tracked = 'all'
        self.list_fluo_cells = []
        self.rep = 0
        self.reptrig = None
        self.list_budding_cells = []         # list of budding cells via model
        self.timestamp = True                # insert time in pictures
        self.insert_rep = True               # insert iteration index
        self.insert_time_elapsed = True      # insert time_elapsed
        self.insert_BF_rate = True           # insert the acquisition rate
        self.obs_duration = True             # insert the time elapsed for observation
        self.insert_num_pos = True           # insert the scale in the picture
        self.insert_scale = True             # insert the scale in the picture
        self.nb_tracks = 0
        ##
        self.list = []
        self.title = title
        self.num = title
        self.dic_displ_obj = { '4x': 3.9, '10x': 1.560,
                               '20x': 0.780, '40x': 0.390,
                               '60x': 0.260, '100x': 0.156 }  # original
        # budding cells history via segm
        self.dic_buds_hist = defaultdict(lambda: defaultdict(lambda: []))
        self.list_buds_hist_rep = defaultdict(list)
        self.curr_exp = None
        # xaxis for changing sampling rate experiments (in min)
        self.list_time_axis = []
        self.focus_labels()                  # open file for AF_ML direct focus
        # conversion factor from image coord to µm according to the objective
        self.fact_micro = self.dic_displ_obj[self.ol.objective]
        self.delay_xcite = 0.5

    def retrieve_models_infos(self):
        '''
        Retrieve name and Id for the models
        '''
        with open('modules/settings/used_models.yaml') as f_r:
            self.used_models = yaml.load(f_r, Loader=yaml.FullLoader)

    def focus_labels(self):
        '''
        image for direct AFML training
        '''
        try:
            addr_direct_AF_ML = opj('mda_temp', 'monitorings',
                                    'AF', 'imgs_for_AF_ML_direct_training')
            self.ol.addr_labels = opj(addr_direct_AF_ML,
                                      f'labels_pos{self.num}.txt')
            f = open(self.ol.addr_labels, 'w')
            f.close()
        except:
            print('not making focus labels for training set.. ')

    def refocus(self, step=None, debug=[1]):
        '''
        Refocus using the AFML or the ZDC, go to the
         optimal position and update in posxyz step..
        '''
        print(f'**** kind is refocus\n'
              f'for pos{self.num} refocusing with'
              f' {self.kind_focus} ..')
        if 'afml' in self.kind_focus:
            # refocus with AFML
            if 1 in debug:
                print(f'self.step_focus = { self.step_focus }')
                print(f'self.delta_focus = { self.delta_focus }')
                print(f'self.ref_posz = { self.ref_posz }')
                print(f'self.focus_nbsteps = { self.focus_nbsteps }')
                print(f'self.thresh = { self.thresh }')
            try:
                # retrieving step_focus and delta_focus from interface
                self.ol.step_focus = self.step_focus
                self.ol.delta_focus = self.delta_focus
                self.ol.focus_nbsteps = self.focus_nbsteps
                self.ol.thresh = self.thresh
                # using the model selected in the interface
                self.ol.mod_afml = getattr(self, self.mod_afml_used)
                if self.num == 0:
                    ref = self.ref_posz-self.delta_focus
                    print(f'for self.num == 0, ref = { ref }')
                else:
                    ref = self.ref_posz
                if 1 in debug:
                    print(f'Using self.ref_posz = {self.ref_posz}')
                    print(f'Using self.delta_focus = {self.delta_focus}')
                    print(f'Using ref = {ref}')
            except:
                print('self.step_focus is not defined.. ')
            self.ref_posz = self.ol.afml_refocus(ref,
                                                 num=self.num,
                                                 rep=self.rep)
            print(f'self.ref_posz after refocus is { self.ref_posz }')
        elif self.kind_focus == 'zdc':
            self.ref_posz = self.ol.zdc_refocus()        # refocus with ZDC
        sleep(1)
        try:
            # updating z position in posxyz step
            self.list_steps['posxyz'].val[2] = self.ref_posz
        except:
            self.z = self.ref_posz    # updating z position for free mda case

    def goto_xy(self, debug=[1]):
        '''
        Set Prior absolute position
        '''
        print(f'in goto_xy, moving to pos {self.x, self.y}')
        # go to the position (x,y)
        self.pr.absolute_move_to(self.x, self.y)
        sleep(1)
        if 1 in debug:
            x = self.pr.ask_pos('x')
            y = self.pr.ask_pos('y')
            print(f'in goto_xy, after move, at pos {x},{y} ')

    def positionxyz(self, step, debug=[0]):
        '''
        Set Prior absolute position
        '''
        if 0 in debug:
            print(f'### In positionxyz !!!')
        print(f'### step.val is  {step.val} ')
        if step.val[0] != step.val[1]:
            # go to the position (x,y)
            self.pr.absolute_move_to(step.val[0], step.val[1])
            # go to pos z
            self.ol.set_zpos(step.val[2])
            print(f'moved to pos {step.val[0]}µm, '
                  ' {step.val[1]}µm, {step.val[2]}')
        else:
            print(Fore.RED + f'*********** Issue, in positionxy, '
                  ' x, y are identical.. !!!  ************')
            print(Style.RESET_ALL)
        sleep(1)
        if self.rep == 0:
            self.x0, self.y0, self.z0 = step.val[0], step.val[1], step.val[2]
            print(f'### Registered position self.x0={self.x0}, '
                  f'self.y0={self.y0}, self.z0={self.z0}  ')

    def prepare_channels(self):    # Prepare the channels before BF and fluo
        '''
        Apply the Cooled "settings channels" for the position
        '''
        self.co.prepare_channels(self.chan_set['COOL'])

    def retrieve_dic_chan(self, step, kind_fluo, debug=[]):
        '''
        Retrieve the settings channels
        '''
        if type(step.val) != list:
            step.val = [step.val]
        for SC in step.val:
            try:
                curr_SC = SC['name']        # settings channels name
                ET = SC['exp_time']
            except:
                curr_SC = SC
                ET = 300
            # if kind_fluo.upper() in curr_SC:
            if 0 in debug:
                print(f"In position, curr_SC is {curr_SC} ")
                print(f'step.val is {step.val} ')
            try:
                # SC yaml file
                addr_SC = self.mda.settings_folder\
                          / 'settings_channels' / f"{curr_SC}.yaml"
                if 1 in debug:
                    print(f'addr_SC is {addr_SC} ')
                with open(addr_SC) as f_r:                           # current SC
                    # Settings channels dictionary
                    dic_chan = yaml.load(f_r, Loader=yaml.FullLoader)
            except:
                print(f"No curr_SC with name {curr_SC} !!!")
            if 2 in debug:
                print(f'######### dic_chan is {dic_chan}')

        return ET, dic_chan

    def define_filt_kind_with_name(self, dic_chan):
        '''
        Return filt and kind_fluo from the SC name
        IF the filter is not defined in the Settings Channels !!!
        '''
        # used in free mda with tree
        if 'RFP' in dic_chan['name_set_chan']:
            filt = 5
            kind_fluo = 'rfp'
        elif 'GFP' in dic_chan['name_set_chan']:
            filt = 3
            kind_fluo = 'gfp'
        elif 'YFP' in dic_chan['name_set_chan']:
            filt = 6
            kind_fluo = 'yfp'

        return filt, kind_fluo

    def img_dmd_adapt_size(self, addr_img_dmd):
        '''
        Adapt the image size for the DMD
        '''
        img = cv2.imread(addr_img_dmd)
        img = cv2.resize(img, (800, 600))
        cv2.imwrite(addr_img_dmd, img)

    def project_dmd_image(self, mask_exp_time, debug=[]):
        '''
        Load and project the image with the DMD device
        '''
        curr_dir = os.getcwd()
        # change path to .exe
        os.chdir(f'{curr_dir}/modules/devices/DMD/mosaic')
        print(f'Current folder is {os.getcwd()}')
        if 0 in debug:
            print(f'Project the mask during {mask_exp_time} seconds')
        # Asynchronous subprocess
        subprocess.Popen(['mosaic_img.exe', f'{mask_exp_time}'])
        # return to the original path
        os.chdir(curr_dir)

    def change_mask(self, mask, debug=[0]):
        '''
        Replace the image for the mask
        '''
        addr_img_dmd = 'modules/devices/DMD/mosaic/image_for_mosaic.png'
        addr_mask_interf = f'interface/static/dmd/img_calib/{mask}.png'
        if 0 in debug:
            print(f'addr_mask_interf : {addr_mask_interf} !!! ')
        sh.copy(addr_mask_interf, addr_img_dmd)
        self.img_dmd_adapt_size(addr_img_dmd)

    def trigger_dmd_image(self, mask, mask_exp_time, debug=[0, 1]):
        '''
        Change the image and project during mask exposure time
        '''
        if 0 in debug:
            print(f'In trigger_dmd_image !!! ')
            print(f'Sending  mask {mask} to DMD !!! ')
        self.change_mask(mask)
        self.project_dmd_image(mask_exp_time)

    def taking_picture_fluo(self, step=None, rep=None,
                                  dic_chan=None, exp_time=300,
                                  mask=None, mask_exp_time=None,
                                  kind_fluo=None, debug=[0,2]):
        '''
        Taking a picture in fluorescence
        '''
        if 0 in debug:
            print(f'Using mask {mask} ...')
        if not rep:
            rep = self.rep
        if step:
            kind_fluo = step.kind_fluo
            mask = step.mask
            mask_exp_time = step.mask_exp_time
            if 1 in debug:
                print(f'######## In taking_picture_fluo ')
                print(f'kind_fluo is {kind_fluo} ')
                print(f'step.val is {step.val} ')
            # Retrieve SC and ET
            exp_time, dic_chan = self.retrieve_dic_chan(step, kind_fluo)

        if 'filter' in dic_chan.keys():
            filt = int(dic_chan['filter'])           # if filter is defined
        else:
            filt, kind_fluo = self.define_filt_kind_with_name(dic_chan)

        # if mask

        if mask:
            # If there is a mask, the fluo is only performed with XCite
            xcite_intens = dic_chan['Xcite']
            if 2 in debug:
                print(f'using the DMD with the mask {mask}'
                      f' during {mask_exp_time} seconds')
                print(f'Will use for XCite, wheel filter num {filt} ')
                print(f'xcite_intens {xcite_intens} ')
            # Set the intensity of the XCite device..
            self.xc.set_intens_level(xcite_intens)
            # set the filter for the fluo with Xcite
            self.ol.set_wheel_filter(filt)
            # close the BF
            self.ol.set_shutter(shut='off')
        else:
            # prepare fluo
            sleep(1)
            # wheel filter for corresponding fluo
            self.ol.set_wheel_filter(filt)
            # shutter µscope off
            self.ol.set_shutter(shut='off')
            # time for filter to be in place
            sleep(2)
            ##
            # free and predef
            self.co.set(dic_chan['COOL'])

        ## take pic

        if not kind_fluo:
            kind_fluo = "fluo1"
        name_pic, addr_pic = self.incr_name(*self.name_pic(rep,
                                            kind_fluo=f'_{kind_fluo}'))
        print(f'in taking_picture_fluo, addr_pic is {addr_pic}')
        print(f'exp_time is  {exp_time} ms')
        if mask:
            print('triggering the dmd')
            apply_calib(mask)
            self.trigger_dmd_image(mask, mask_exp_time)
            sleep(5)                     # delay for loading and triggering
            print('shut Xcite on')
            self.xc.shut_on()
            sleep(self.delay_xcite)

        # take the fluo pic
        # camera exposure time is a blocking operation
        self.ev.take_pic(addr_pic, bpp=8, exp_time=exp_time, allow_contrast=False)

        print(f'filt for fluo is {filt}')

        if mask:
            # stop using the Xcite
            sleep(int(mask_exp_time))
            # return to 0 and shut off
            self.xc.set_intens_level(0)
            sleep(self.delay_xcite)
            self.xc.shut_off()
            sleep(self.delay_xcite)
            print('Normally intensity is 0 and shutter off !!!')

        # set off

        # set all the channels off
        set_fluo_off = f'CSF'
        print(f'set_fluo_off {set_fluo_off}')
        self.co.emit(set_fluo_off)
        self.save_fluo_pic(addr_pic, rep, kind_fluo)
        self.ol.set_wheel_filter(1) # return to BF

    def incr_name(self, name_pic, addr_pic, debug=[0,1,2]):
        '''
        increment index for fluo until the file does not yet exist..
        '''
        if 0 in debug:
            print(f'name_pic is {name_pic}')
            print(f'addr_pic is {addr_pic}')
        new_name_pic = name_pic
        while os.path.exists(addr_pic):
            res = int(re.findall('fluo(\\d+)_', name_pic)[0])
            new_name_pic = name_pic.replace(f'fluo{res}_', f'fluo{res+1}_')
            if 1 in debug:
                print(f'new_name_pic is {new_name_pic}')

            addr_pic = addr_pic.replace(name_pic, new_name_pic)
            if 2 in debug:
                print(f'addr_pic is {addr_pic}')
        return new_name_pic, addr_pic

    def save_fluo_pic(self, addr_pic, rep, kind_fluo, debug=[0]):
        '''
        Save picture with fluorescence
        '''
        # copy in test/movie
        if 0 in debug:
            print(f'In save_fluo_pic, kind_fluo is {kind_fluo}')
        self.copy_pic_in_test(addr_pic, rep, fluo=kind_fluo)
        if kind_fluo == 'rfp':
            # passing from tiff to png in folder imgs_for_BF_RFP_videos
            self.img_video_from_tiff_to_png(rep, targ='BF_fluo_video')
        elif kind_fluo == 'gfp':
            # passing from tiff to png in folder imgs_for_GFP_videos
            self.img_video_from_tiff_to_png(rep, targ='GFP_video')
        elif kind_fluo == 'yfp':
            # passing from tiff to png in folder imgs_for_GFP_videos
            self.img_video_from_tiff_to_png(rep, targ='YFP_video')

    def debug_take_pic(self):
        '''
        debug for BF take pic..
        '''
        posz = self.ol.ask_zpos()
        print(f'current posz is {posz}')
        posx = self.pr.ask_pos('x')
        posy = self.pr.ask_pos('y')
        print(f'current pos is {posx},{posy}')

    def copy_pic_in_test(self, addr_pic, rep, fluo=None, debug=[]):
        '''
        Copy pic from addr_pic to test/movie folder
        '''
        if fluo:
            dest = opj(os.getcwd(), 'test', 'movie',
                       f'frame{self.num}_{fluo}_t{rep}.tiff')
        else:
            dest = opj(os.getcwd(), 'test', 'movie',
                       f'frame{self.num}_t{rep}.tiff')
        if 0 in debug:
            print(f'image copied in {dest}')
        sh.copy(addr_pic, dest)

    def copy_pic_in_curr_pic(self, addr_pic, debug=[]):
        '''
        Copy BF pic in : interface/static/curr_pic
        '''
        if 0 in debug:
            print('copy_pic_in_curr_pic')
        dest = opj(os.getcwd(), 'interface', 'static',
                   'curr_pic', f'frame{self.num}.tiff')
        sh.copy(addr_pic, dest)

    def copy_pic_BF(self, addr_pic, rep, debug=[1]):
        '''
        Copy BF pic in : interface/static/mda_pics/imgs_pos
        and also in mda_temp/monitorings/BF
        Passing from tiff to png
        '''
        curr_pic_BF = f'frame{self.num}'
        dest1 = opj(os.getcwd(), 'interface', 'static',
                   'mda_pics', 'imgs_pos', f'{curr_pic_BF}.png')
        dest2 = opj(os.getcwd(), 'interface', 'static',
                    f'{self.dir_mda_temp}', 'monitorings', 'BF', f'frame{self.num}_t{rep}.png')
        img = cv2.imread(addr_pic)
        try:
            cv2.imwrite(dest1, img)
        except:
            if 0 in debug:
                print('Cannot write BF pic in imgs_pos')
        try:
            cv2.imwrite(dest2, img)
        except:
            if 1 in debug:
                print('Cannot write BF pic in monitorings/BF')

    def prepare_BF(self, delay_shut=1, debug=[]):
        '''
        Prepare the wheel filter and the shutter for the BF
        '''
        if 1 in debug:
            print('Prepare wheel filter for BF..')
            print(f'self.ol.curr_wheel is {self.ol.curr_wheel}')
        if self.ol.curr_wheel != 1:
            self.ol.set_wheel_filter(1)     # wheel filter
            # temporization for the wheel filter to get correctly in place
            sleep(2)
            if 1 in debug:
                print('Filter in place..')
        if not self.ol.shut:
            self.ol.set_shutter(shut='on')                    # shutter
            sleep(delay_shut)          # delay between shutter and camera

    def make_blur_score(self, addr_pic, debug=[]):
        '''
        Calculate the score for bluriness
        '''
        img = cv2.imread(addr_pic)
        self.blur = round(cv2.Laplacian(img.astype('uint8'), 3).var(), 1)
        if 0 in debug:
            print(f'bluriness estimated as {self.blur}')

    def prepare_imgs_for_BF_fluo(self, rep, debug=[]):
        '''
        Prepare the images for the video mixing BF and fluo
        '''
        if 0 in debug:
            print('**************  in prepare_imgs_for_BF_fluo '
                                                '  **************')
        addr_png = opj(self.dir_mda_temp, 'imgs_for_videos',
                       f'frame{self.num}_t{rep}.png')
        addr_BF_fluo = opj(self.dir_mda_temp, 'imgs_for_BF_RFP_videos')
        sh.copy(addr_png, addr_BF_fluo)             # copy BF images
        ####
        if 1 in debug:
            print(f'Copied {addr_png} in {addr_BF_fluo} !!!')
        addr_tiff_pos = opj(os.getcwd(), 'test', 'movie',
                            f'frame{self.num}_rfp_t{rep}.tiff')
        addr_png_pos = opj(self.dir_mda_temp, 'imgs_for_BF_RFP_videos',
                           opb(addr_tiff_pos)[:-5] + '.png')
        if 2 in debug:
            print(f'addr_tiff_pos {addr_tiff_pos}, '
                  'addr_png_pos {addr_png_pos} !!!')
        return addr_tiff_pos, addr_png_pos

    def prepare_imgs_for_GFP(self, rep, debug=[]):
        '''
        Prepare the images for the video GFP
        '''
        if 0 in debug:
            print('**************  in prepare_imgs_for_GFP  **************')
        addr_GFP = opj(self.dir_mda_temp, 'imgs_for_GFP_videos')
        ####
        addr_tiff_pos = opj(os.getcwd(), 'test', 'movie',
                            f'frame{self.num}_gfp_t{rep}.tiff')
        addr_png_pos = opj(self.dir_mda_temp,
                           'imgs_for_GFP_videos',
                           opb(addr_tiff_pos)[:-5] + '.png')
        if 2 in debug:
            print(f'addr_tiff_pos {addr_tiff_pos}, '
                  ' addr_png_pos {addr_png_pos} !!!')
        return addr_tiff_pos, addr_png_pos

    def img_video_from_tiff_to_png(self, rep, targ='mda_temp'):
        '''
        Save images in png format for video
        take from test/movie and put it in "temp_mda/imgs_for_videos"
        '''
        if targ == 'BF_video':
            addr_tiff_pos = opj(os.getcwd(), 'test', 'movie',
                                f'frame{self.num}_t{rep}.tiff')
            addr_png_pos = opj(self.dir_mda_temp, 'imgs_for_videos',
                               opb(addr_tiff_pos)[:-5] + '.png')

        if targ == 'BF_fluo_video':
            try:
                addr_tiff_pos, addr_png_pos = self.prepare_imgs_for_BF_fluo(rep)
            except:
                print('Cannot execute self.prepare_imgs_for_BF_fluo(rep) !!')

        if targ == 'GFP_video':
            addr_tiff_pos, addr_png_pos = self.prepare_imgs_for_GFP(rep)

        elif targ == 'current':
            path_curr_pic = opj(os.getcwd(), 'interface', 'static', 'curr_pic')
            addr_tiff_pos = opj(path_curr_pic, f'frame{self.num}.tiff')
            addr_png_pos = opj(path_curr_pic, opb(addr_tiff_pos)[:-5] + '.png')

        try:
            img = cv2.imread(addr_tiff_pos)
            cv2.imwrite(addr_png_pos, img)
        except:
            print('Cannot save tiff as png !!')

    def actions_after_BF_pic(self, addr_pic, rep, debug=[]):
        '''
        Handle pictures
        '''
        if 0 in debug:
            print('### actions_after_BF_pic !!')
        self.copy_pic_in_test(addr_pic, rep)        # folder for processings
        self.copy_pic_in_curr_pic(addr_pic)         # copy in current pic
        # folder for following the positions
        self.copy_pic_BF(addr_pic, rep)
        # passing from tiff to png in folder imgs_for_videos
        self.img_video_from_tiff_to_png(rep, targ='BF_video')
        # passing from tiff to png for live mode
        self.img_video_from_tiff_to_png(rep, targ='current')

    def make_contour_tracked(self):
        '''
        '''
        cntr_tracked = self.curr_contours[self.chosen_numcell]
        # cntr_tracked = self.curr_contours[self.index_pos_nearest_to_center]
        # show contour of the tracked cell
        self.curr_pic_vid = cv2.drawContours(self.curr_pic_vid,
                                             [cntr_tracked], -1,
                                             (0, 0, 254), 1)
        # show contour of the tracked cell in RFP
        self.curr_pic_fluo_vid = cv2.drawContours(self.curr_pic_fluo_vid,
                                                  [cntr_tracked], -1,
                                                  (254, 0, 0), 1)

    def track_mark(self, image_center=False, contour=True, debug=[1]):
        '''
        Mark for indicating the tracking
        Indicate the center of the picture and make
         the contours for BF and fluo
        Show the tracked cell..
        '''
        if image_center:
            center, radius, color = (256, 256), 2, (255, 0, 0)
            # indicate the cell tracked with a circle
            self.curr_pic_vid = cv2.circle(self.curr_pic_vid,
                                center, radius, color, -1)
        if contour:
            if 1 in debug:
                print('draw contour of the dragged object..')
            try:
                #  contour of the tracked cell
                self.make_contour_tracked()
            except:
                print('*** Cannot plot the contour of the tracked cell ***')

    def insert_text(self, img, text, size=0.4, pos=(10, 500), col=(0, 255, 0)):
        '''
        Insert text in image
        '''
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 1
        cv2.putText(img, str(text), pos, font,
                    size, col, thickness, cv2.LINE_AA)

    def date(self):
        '''
        Return a string with day, month, year, hour, minute and seconds
        '''
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")  # -%H-%M
        return dt_string

    def timestamp_now(self):
        '''
        Return the timestamp for current time
        '''
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        return timestamp

    def time_elapsed(self):
        '''
        Time elapsed from the beginning of the MDA, in minutes
        '''
        now = datetime.now()
        time_elapsed = str(round((now - self.first_time).seconds/60, 2))
        return time_elapsed

    def copy_BF_vid_in_BF_RFP(self, addr_pic):
        '''
        Copy BF pics in "imgs_for_BF_RFP_videos"
                folder for producing BF + RFP movie
        '''
        addr_BF_fluo_png_pos = opj(self.dir_mda_temp,
                                   'imgs_for_BF_RFP_videos', opb(addr_pic))
        sh.copy(addr_pic, addr_BF_fluo_png_pos)

    def insert_time_marks(self, pic):
        '''
        Insert the date, the time elapsed and
         the iteration number in the picture
        '''
        if self.timestamp:
            # insert date with hours, min, sec
            self.insert_text(pic, self.date(), pos=(10, 500))
        if self.insert_rep:
            # insert time elapsed in minutes
            self.insert_text(pic, 'rep ' + str(self.rep),
                                  pos=(450, 500), col=(0, 255, 0))
        if self.insert_time_elapsed:
            # insert index of the picture
            self.insert_text(pic, 'elapsed ' +
                                  self.time_elapsed() + ' min',
                                  pos=(250, 500), col=(0, 255, 0))
        if self.insert_BF_rate:
            # insert the current BF rate
            self.insert_text(pic, 'BF rate ' +
                                  str(self.mda.delay) + ' min',
                                  pos=(10, 20), col=(255, 236, 179))
        try:
            if self.obs_duration:
                curr_time = time.time()
                tobs_elapsed = round((curr_time -
                                      self.mda.trig_obs_time)/60, 1)
                # insert the duration of the observation and its index
                self.insert_text(pic, f'obs num {self.nb_tracks} since ' +
                                      str(tobs_elapsed) + ' min',
                                      pos=(200, 20), col=(255, 255, 0))
        except:
            print('Cannot show observation duration..')

    def insert_scale_bar(self, pic, pos, h=4, w=50,
                         thick=3, col=(255, 255, 0)):
        '''
        Bar for indicating the size
        '''
        p0, p1 = pos[0]-10, pos[1]+10                           # bar position
        cv2.rectangle(pic, (p0, p1), (p0+w, p1-h), col, thick)     # scale bar

    def insert_image_scale(self, pic, pos=(10, 10)):
        '''
        Insert the scale of the image for the current objective in use
        '''
        dic_scale = {'20x': '90um', '40x': '45um',
                     '60x': '30um', '100x': '18um'}
        # text according to the objective in use
        # size of the bar in µm
        size_scale = dic_scale[self.ol.objective]
        # insert the duration of the observation
        self.insert_text(pic, size_scale, pos=pos, col=(255, 255, 0))
        self.insert_scale_bar(pic, pos)      # scale bar

    def insert_infos(self, pic):
        '''
        Insert infos
        '''
        if self.insert_num_pos:
            # insert pos index
            self.insert_text(pic, 'pos ' + str(self.num),
                                  pos=(450, 20), col=(255, 255, 0))
        # insert scale information
        if self.insert_scale:
            self.insert_image_scale(pic, pos=(20, 470))

    def enrich_pic(self, rep, debug=[1]):
        '''
        Add timestamp, tracking mark etc to the picture..
        '''
        # use BF pic for video in .png
        name_pic, addr_pic = self.name_pic_vid(rep)
        if 1 in debug:
            print('enriching the current pic !!!')
        self.curr_pic_vid = cv2.imread(addr_pic)
        #####
        try:
            _, addr_pic_fluo_vid = self.name_pic_vid(rep, kind_fluo='_rfp')
            self.curr_pic_fluo_vid = cv2.imread(addr_pic_fluo_vid)
        except:
            pass
        #####
        # insert time informations
        self.insert_time_marks(self.curr_pic_vid)
        # insert various infos
        self.insert_infos(self.curr_pic_vid)
        # center of the image and contours of the tracked elements
        if self.tracking:
            self.track_mark()
        print('pic taken..')
        if 2 in debug:
            # address for enriched picture
            print(f'addr_pic is {addr_pic}')
        cv2.imwrite(addr_pic, self.curr_pic_vid)    # save BF pic with infos
        try:
            # save fluo pic with infos
            cv2.imwrite(addr_pic_fluo_vid, self.curr_pic_fluo_vid)
        except:
            print(f'Cannot write in {addr_pic_fluo_vid} ')
        # copy BF for BF_RFP movie
        self.copy_BF_vid_in_BF_RFP(addr_pic)

    def make_mda_time(self):
        '''
        '''
        ttot = round(time.time()-g.mda_time_start,1)
        ttot_hrs = int(ttot//3600)
        sec_rest_hrs = int(ttot%3600)
        ttot_min = int(sec_rest_hrs//60)
        sec_rest_min = int(sec_rest_hrs%60)
        ##
        mdat_elapsed = f'{ttot_hrs}h{ttot_min}m{sec_rest_min}s'

        return mdat_elapsed

    def save_time_BF(self, debug=[]):
        '''
        Dictionary with time for each repetition for each position
        '''
        if 0 in debug:
            print(f'g.mda_time_start is {g.mda_time_start}')
        if g.mda_time_start:
            mdat_elapsed = self.make_mda_time()
        addr_pic_times = opj(self.dir_mda_temp, 'monitorings', 'pic_time.yaml')
        with open(addr_pic_times) as f_r:
            dic_pic_time = yaml.load(f_r, Loader=yaml.FullLoader)
            if 1 in debug:
                print(f'after open, dic_pic_time is {dic_pic_time}')
        with open(addr_pic_times, "w") as f_w:
            try:
                dic_pic_time[str(self.rep)][str(self.num)] = mdat_elapsed
            except:
                dic_pic_time[str(self.rep)] = {}
                dic_pic_time[str(self.rep)][str(self.num)] = mdat_elapsed
            if 2 in debug:
                print(f'dic_pic_time is {dic_pic_time}')
            yaml.dump(dic_pic_time, f_w)

    def taking_picture(self, step=None, rep=None, exp_time=100, debug=[2]):
        '''
        Take a picture in BF mode
        step : object with info about the actions to perform
        rep : index of repetition
        '''
        print('**** kind is cam, taking pic..')
        if not rep:
            rep = self.rep
        if 0 in debug:
            print('..taking a picture..')
        if 2 in debug:
            print(f'Using exposure time : {exp_time} ')
        if 1 in debug:
            self.debug_take_pic()
        self.prepare_BF()
        name_pic, addr_pic = self.name_pic(rep)
        # take the pic, 8 bytes per pixel, 500 ms of exposure
        # allow_contrast=True
        self.ol.set_shutter(shut='on')
        # take BF pic
        # autocontrast driven from interface..
        self.ev.take_pic(addr_pic, bpp=8, exp_time=exp_time,
                         allow_contrast=self.ev.autocontrast)
        self.save_time_BF()
        ## close the shutter
        self.ol.set_shutter(shut='off')
        #
        self.list_time_axis += [float(self.time_elapsed())]
        self.actions_after_BF_pic(addr_pic, rep)
        ##
        emit('take_pic', '')
        server.sleep(ts_sleep)

    def delay(self, time_delay):
        '''
        Delay expressed in the Tree in milliseconds
        '''
        sleep(time_delay/1000)

    def name_pic(self, rep, kind_fluo=''):
        '''
        name and address for pictures
        rep : index of repetition
        kind_fluo : 'rfp', 'gfp' etc..
        '''
        name_pic = f'frame{self.num}{kind_fluo}_t{rep}.tiff'
        addr_pic = opj(self.dir_mda_temp, name_pic)
        return name_pic, addr_pic

    def name_pic_vid(self, rep, kind_fluo='', debug=[0]):
        '''
        name and address for pictures
        rep : index of repetition
        kind_fluo : 'rfp', 'gfp' etc..
        '''
        #name_fluo = '_' + kind_fluo
        name_pic = f'frame{self.num}{kind_fluo}_t{rep}.png'
        if 0 in debug:
            print(f'*** name_pic is {name_pic}')
        if len(kind_fluo) == 0:
            addr_pic = opj(self.dir_mda_temp, 'imgs_for_videos', name_pic)
        elif kind_fluo == '_rfp':
            addr_pic = opj(self.dir_mda_temp,
                           'imgs_for_BF_RFP_videos', name_pic)
        return name_pic, addr_pic

    def mask_from_cntr(self, cntr, mask=None, debug=[]):
        '''
        Find mask from contour
        '''
        try:
            _ = mask.shape
        except:
            mask = np.zeros((self.size, self.size))
            if 1 in debug:
                print('### create the mask !!!')
        if 1 in debug:
            print(f'### type(cntr) {cntr} ')
        # save mask of the segmentation
        cv2.drawContours(mask, cntr, -1, (255, 255, 255), -1)
        return mask

    def pos_from_cntr(self, c):
        '''
        Extract the position from the contour
        '''
        x, y, w, h = cv2.boundingRect(c)
        pos = (int(x + w/2), int(y + h/2))  # find position
        return pos

    def message_analysis(self, t0, t1, debug=[]):
        '''
        Message at the end of analysis
        t0, t1 : beginning and ending times for cells counting..
        '''
        print(Fore.RED + f'###  nb of cells for pos'
              f' {self.num} at rep {self.rep} is {self.nb_cells} !!!!')
        print(Style.RESET_ALL)
        print(f'time elapsed for iteration {self.rep} for '
              ' performing all the operations after '
              f' acquisition is : {round(t1-t0,2)} s')
        try:
            print(f"self.num_gate is {self.num_gate} !!!")
        except:
            pass

    def search_event(self, rep, debug=[0, 1, 2]):
        '''
        Looking for event
        '''
        if 0 in debug:
            print(f'search_event for pos {self.num} !!!!')
        if self.event.name in ['rfp', 'gfp']:
            self.find_fluo(rep)
        elif self.event.name == 'bud':
            self.find_buds(rep)
        elif self.event.name == 'bud_with_size':
            self.find_buds_with_size(rep)
        if 1 in debug:
            print(f'#### Searching event name {self.event.name}')
        if 2 in debug:
            print(f'#### iteration is  {rep}')

    def cells_analysis(self, rep, curves=False, debug=[]):
        '''
        rep : index of repetition
        '''
        print('**** kind is cells_analysis..')
        self.dir_test = opj(os.getcwd(), 'test', 'movie')
        t0 = time.time()
        for f in os.listdir(self.dir_test):
            # make prediction of the unique image in test/movie
            self.predict_and_save(f)
        # tracking must be specified
        if self.track_in_analysis:
            try:
                # track the cells with the main segmentation model (eg ep5_v3)
                self.track_BF(rep)
            except:
                print(Fore.RED + 'Cannot track, issue with tracking')
                print(Style.RESET_ALL)
            # find the cell the nearest from center
            self.find_nearest_from_center()
        if self.curr_exp == 'hog1':
            if curves:
                self.hog1_curves(rep)
        if self.event.exists:                # detected an event
            if not self.event.happened:      # if the event has not yet occured
                self.search_event(rep)       # search for the event
        t1 = time.time()
        self.message_analysis(t0, t1)

    def make_steps(self, rep, ind_pos, debug=[1]):
        '''
        Perform the successive steps for each position
        '''
        self.rep = rep
        self.num = ind_pos
        # if self.ol.offset or self.ol.offset == 0 :        # offset decided
        for _, step in self.list_steps.items():
            if step:
                if 1 in debug:
                    print(f'##### current step is {step.kind} ')
                if step.kind == 'posxyz':
                    self.positionxyz(step)               # go to x,y,z
                elif step.kind == 'chan_set':
                    self.prepare_channels(step)          # Setting channels
                elif step.kind == 'cam':
                    self.taking_picture(step, rep)       # take a picture in BF
                elif step.kind == 'fluo':
                    # take a picture in fluo
                    self.taking_picture_fluo(step, rep)
                elif step.kind == 'refocus':
                    self.refocus(step)                 # refocus
                elif step.kind == 'cells_analysis':
                    # perform cells analysis, retroaction
                    self.cells_analysis(rep)
        self.enrich_pic(rep)

    # loop for augmented MDA

    def loop(self, rep, event, debug=[]):
        '''
        Loop in position's elements, reading the Tree
        '''
        print('----------------')
        print(f'dealing with position : {self.title} ')
        self.event = event
        self.event.exists = True
        if 1 in debug:
            print(f'**** free_mda  pos{self.num} self.list is {self.list}')
        for elem in self.list:
            if type(elem) == list:
                if elem[0].__name__ == 'taking_picture_fluo':
                    if len(elem) == 5:
                        # if there is a mask,
                        # call taking_picture_fluo with 4 args
                        elem[0](dic_chan=elem[1],
                                exp_time=elem[2],
                                mask=elem[3],
                                mask_exp_time=elem[4])
                    else:
                        # no mask
                        elem[0](dic_chan=elem[1],
                                exp_time=elem[2])
                elif elem[0].__name__ == 'taking_picture':
                    elem[0](exp_time=elem[1])
                    self.cells_analysis(rep)
                    if 2 in debug:
                        print(f'Using exposure time {elem[1]} for BF')
                elif elem[0].__name__ == 'delay':
                    elem[0](elem[1])
            else:
                elem()                      # elem is directly a function
            if elem == self.list[-1]:
                self.rep += 1               # increment the counter if elem is
