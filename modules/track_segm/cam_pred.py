'''

Make predictions and find contours with image acquired with camera..
Used in Mda and Live modes

'''

import os
# Tensorflow verbosity, tensorflow mute
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # or any {'0', '1', '2'}

try:
    from modules.util_server import find_platform, chose_server
    platf = find_platform()
    server = chose_server(platf)
    from modules.util_misc import *
except:
    print("no socket")

from pathlib import Path
# console colors
from colorama import Fore, Style
# tensorflow
from tensorflow.keras import models
import tensorflow.keras as tfk
# Tracking
from modules.modules_mda.tracking import TRACK as TR
import shutil as sh
import yaml
import re
import numpy as np
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

import cv2


class CAM_PRED(TR):
    '''
    Film and predict
    '''
    def __init__(self, dir_pred=None,
                       mode='mda',
                       events=True,
                       debug=[]):
        '''
        mode: mda or predefined_mda
        '''
        TR.__init__(self)
        if 0 in debug:
            print(f'########### mode is {mode} ')
        self.dir_pred = dir_pred
        self.mode = mode
        self.load_curr_model()
        self.list_nb_cells = []   # list of nb of cells detected in the image
        self.nb_cells = 0
        # list of nb of cells events detected in the image
        self.list_nb_cells_events = []
        self.nb_cells_events = 0
        self.num_acq = 0                     # acquisition index
        self.freq_track = 20                 # tracking frequency in live mode
        self.all_cntrs = {}
        self.track_method = 2                # 2 --> basic method
        self.erode_after_pred = False
        self.show_num_cell = True
        self.which_tracked = 'all'
        self.curr_pred = 'BF'      # initialize prediction with BF segmentation
        if events:
            self.load_event_model()     # load the model for event prediction

    def load_curr_model(self, debug=[]):
        '''
        Load the current model
        '''
        if 0 in debug:
            print('## In load_curr_model !!!!!! ')
        with open('modules/settings/curr_model.yaml') as f_r:
            curr_mod = yaml.load(f_r, Loader=yaml.FullLoader)
            if 0 in debug:
                print(f'####** curr_mod = {curr_mod} ')
        # load the main cell segmentation model
        self.curr_mod = self.load_model(curr_mod)
        if 1 in debug:
            print(f'################ In cam pred, curr_mod {curr_mod}')

    def load_event_model(self, debug=[]):
        '''
        Load the model for event detection
        '''
        with open('modules/settings/event_model.yaml') as f_r:
            ev_mod = yaml.load(f_r, Loader=yaml.FullLoader)
            # event model
            self.ev_mod = self.load_model(ev_mod)
        if 0 in debug:
            print(f'################ In cam pred, event model {ev_mod}')

    def image_contours(self, img, cntrs, debug=[]):
        '''
        Image with black background and contours
        img : image from which is extracted the size
        cntrs : contours from img
        '''
        if 0 in debug:
            print(f'**** in image_contours !!! ****')
        try:
            h, w = img.shape                                        # OTSU
        except:
            h, w, _ = img.shape
        mask = np.zeros((h, w), np.uint8 )
        # fill contour
        self.img_cntrs = cv2.drawContours(mask, cntrs, -1, (255, 255, 255), -1)
        # contours address for mda mode
        if self.mode == 'mda':
            self.addr_cntrs = opj(self.dir_mda_temp, 'monitorings',
                                  'cntrs', self.predf[:-4] + '_cntrs.png')
        elif self.mode == 'live':
            # contours address for live mode
            self.addr_cntrs = opj(self.dir_pred,
                                  self.predf[:-4] + '_cntrs.png')
        if 1 in debug:
            print(f'self.addr_cntrs is {self.addr_cntrs}')
        cv2.imwrite(self.addr_cntrs, self.img_cntrs)

    def superimpose_image_contours(self, debug=[]):
        '''
        Superimpose contours and orginal image
        '''
        if self.mode == 'mda':
            print(f'self.addr_pred_img is {self.addr_pred_img}')
            # save prediction
            img = cv2.imread(self.addr_pred_img)
        if self.mode == 'live':
            if 0 in debug:
                print(f'self.addr_img_BF is {self.addr_img_BF}')
            # BF
            img = cv2.imread(self.addr_img_BF)
        if 1 in debug:
            print(f'self.addr_cntrs is {self.addr_cntrs}')
        # contours
        img_cntrs = cv2.imread(self.addr_cntrs)
        ##
        # add contour on the cells
        added_image = cv2.addWeighted(img, 0.9, img_cntrs, 0.5, 0)
        if self.mode == 'mda':
            # addr superimposed contours
            addr_superp = opj(self.dir_mda_temp, 'monitorings',
                              'superp_cntrs', self.predf[:-4] + '_superp.png')
        elif self.mode == 'live':
            addr_superp = opj(self.dir_pred, self.predf[:-4] + '_superp.png')
        # save BF with superimposed contours
        cv2.imwrite(addr_superp, added_image)

    def bytescaling(self, data, cmin=None, cmax=None, high=255, low=0):
        '''
        bytescaling for OTSU
        '''
        if data.dtype == np.uint8:
            return data
        if high > 255:
            high = 255
        if low < 0:
            low = 0
        if high < low:
            raise ValueError("`high` should be"
                             " greater than or equal to `low`.")
        if cmin is None:
            cmin = data.min()
        if cmax is None:
            cmax = data.max()
        cscale = cmax - cmin
        if cscale == 0:
            cscale = 1
        scale = float(high - low) / cscale
        bytedata = (data - cmin) * scale + low
        return (bytedata.astype(np.uint8))

    def filter2D(self, img):
        '''
        filter2D for OTSU
        '''
        kernel = np.array((
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, 24, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1]), dtype="int")
        img = cv2.filter2D(img, -1, kernel)
        return img

    def counting_BF_cells(self, nb_cntrs, debug=[]):
        '''
        Count the cells in BF image
        '''

        if 2 in debug:
            print('### refreshing number of cells')
        self.nb_cells = nb_cntrs
        # list of nb of cells for each position
        self.list_nb_cells.append(self.nb_cells)
        if 1 in debug:
            print(f'self.nb_cells in counting_BF_cells is {self.nb_cells} ')

    def counting_events(self, nb_cntrs):
        '''
        Count the event
        '''
        self.nb_cells_events = nb_cntrs
        self.list_nb_cells_events.append(self.nb_cells_events)

    def counting_cells(self, contours, debug=[]):
        '''
        Counting cells (BF or events)
        Using a protection against big jumps
        '''
        if 1 in debug:
            print(f'### in counting_cells self.curr_pred is {self.curr_pred} ')
        nb_cntrs = len(contours)
        if 2 in debug:
            print(f'nb of contours in counting_cells  is {nb_cntrs}')
        if self.curr_pred == 'BF':
            # count in BF
            self.counting_BF_cells(nb_cntrs)
        elif self.curr_pred == 'events':
            # count the events
            self.counting_events(nb_cntrs)

    def images_from_contours(self, img, contours, debug=[]):
        '''
        Image of contours and superimposed contours for monitoring
        '''
        self.image_contours(img, contours)
        self.superimpose_image_contours()

    def using_contours(self, img, contours):
        '''
        Use contours for producing control images and counting cells
        '''
        self.images_from_contours(img, contours)
        self.counting_cells(contours)

    def find_contours_thresh(self, addr, thr):
        '''
        Find contours with simple thresholding
        '''
        img = cv2.imread(addr)
        # img gray
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, thr, 255, 0)
        contours, hierarchy = cv2.findContours(thresh,
                                               cv2.RETR_TREE,
                                               cv2.CHAIN_APPROX_SIMPLE)[-2:]
        return img, contours

    def find_contours_otsu(self, addr, debug=[]):
        '''
        Find contours with OTSU method
        '''
        img = cv2.imread(addr, 0)
        img = self.bytescaling(img)
        img = cv2.GaussianBlur(img, (5, 5), 0)
        img = self.filter2D(img)         # filtering with kernel..
        ret2, th2 = cv2.threshold(img,
                                  0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        contours, _ = cv2.findContours(th2.copy(),
                                       cv2.RETR_EXTERNAL,
                                       cv2.CHAIN_APPROX_SIMPLE)[-2:]
        return img, contours

    def find_contours_and_count(self, meth='otsu', thr=None, debug=[]):
        '''
        Find contours on prediction image and counts the cells
        By default using OTSU
        '''
        if self.mode == 'mda':
            # addr of pred for mda mode
            addr_pred = opj(self.dir_mda_temp,
                            'monitorings', 'pred', self.predf)
        elif self.mode == 'live':
            # addr of pred for live mode
            addr_pred = opj(self.dir_pred, self.predf)
        if meth == 'otsu':
            # find contours with OTSU method
            img, self.curr_cntrs = self.find_contours_otsu(addr_pred)
        elif meth == 'thresh':
            # find contours by simple thresholding
            img, self.curr_cntrs = self.find_contours_thresh(addr_pred, thr=thr)
        # count the cells etc..
        self.using_contours(img, self.curr_cntrs)

    def save_pred_generic(self, f, pred, kind='pred', debug=[]):
        '''
        Save the predictions
        '''
        if 0 in debug:
            print(Fore.YELLOW + f'### kind prediction is {kind} ')
            print(Style.RESET_ALL)
        self.predf = f"{kind}_{f[:-5]}.png"
        # mda mode
        if self.mode == 'mda':
            self.addr_predf = opj(self.dir_test, self.predf)
        # live mode
        elif self.mode == 'live':
            self.addr_predf = opj(self.dir_pred, self.predf)
        # save prediction
        cv2.imwrite(self.addr_predf, pred)
        if self.mode == 'mda':
            # move prediction to mda_temp folder
            self.move_to_mda_temp(f)
        # count segm 1
        if kind == 'pred_ev':
            self.curr_pred = 'events'
            # contours for events (with threshold) and counting
            self.find_contours_and_count(meth='thresh', thr=127) # meth='thresh', thr=200
        else:
            self.curr_pred = 'BF'
            # make contours and count segmented cells
            # count segm 0
            self.find_contours_and_count(meth='thresh', thr=127)

    def save_pred(self, f, pred, pred_ev=None):
        '''
        Save the predictions
        '''
        try:
            # pred for events
            self.save_pred_generic(f, pred_ev, kind='pred_ev')
        except:
            print('no event to save')
        # pred for cells
        self.save_pred_generic(f, pred, kind='pred')

    def save_nb_cells(self, debug=[]):
        '''
        Save the number of cells for monitoring
        '''
        # yaml addr for nb cells
        self.addr_nb_cells = opj(self.dir_pred, 'nb_cells.yaml')
        # yaml addr for nb of events
        self.addr_nb_events = opj(self.dir_pred, 'nb_events.yaml')
        if self.curr_pred == 'BF':
            # nb of cells
            with open(self.addr_nb_cells, 'w') as f_w:
                yaml.dump(self.nb_cells, f_w)
        # nb of events
        elif self.curr_pred == 'events':
            with open(self.addr_nb_events, 'w') as f_w:
                yaml.dump(self.nb_events, f_w)
        if 1 in debug:
            print(f'self.nb_cells is {self.nb_cells}')

    def load_dict_models(self):
        '''
        Dictionary of the models with their aliases..
        '''
        # yaml file with all the possible models
        addr_models = Path('modules') / 'settings' / 'models.yaml'
        with open(addr_models) as f_r:
            dic_mod = yaml.load(f_r, Loader=yaml.FullLoader)
        return dic_mod

    def load_model(self, mod, debug=[]):
        '''
        mod : name of the model
        ep5_v3 : segmentation model for 100x
        ep15_x20_otsu : segmentation model for 20x
        '''
        dic_mod = self.load_dict_models()
        if 0 in debug:
            print(Fore.YELLOW + f'*** loading {mod} ... ')
            print(Style.RESET_ALL)
        # dic_mod[mod] : model used
        model_loaded = models.load_model(Path('models') / dic_mod[mod])
        if 0 in debug:
            print(f'*** The model {mod} is loaded ***')
        return model_loaded

    def move_to_mda_temp(self, f):
        '''
        Move current prediction to mda_temp folder
        '''
        # image used for prediction
        self.addr_pred_img = opj(self.dir_mda_temp, f)
        try:
            # remove the image in test/movie used for prediction
            os.remove(self.addrf)
        except:
            print(f'probably yet removed {self.addrf} the image before !!')
        sh.move(self.addr_predf, opj(self.dir_mda_temp,
                'monitorings', 'pred', self.predf))   # prediction in mda_temp

    def array_for_pred(self, f):
        '''
        Prepare image format for prediction
        '''
        if self.mode == 'mda':
            self.addrf = opj(self.dir_test, f)       # addr image for prediction
        elif self.mode == 'live':
            self.addrf = opj(self.dir_pred, f)       # addr image for prediction
        self.img = cv2.imread(self.addrf)
        # format array for prediction
        arr = np.array([self.img], dtype=np.float32)/255
        return arr

    def cam_track_BF(self):
        '''
        Track the cells
        '''
        self.img_cam = self.img.copy()
        self.all_cntrs[self.num_acq] = self.curr_cntrs
        # segment and track in BF
        self.cell_tracking(0, [self.curr_cntrs, None])
        name_pic = f'track_frame0.png'
        addr_pic = opj(self.dir_pred, name_pic)
        cv2.imwrite(addr_pic, self.img)

    def predict_basic(self, f, event=True, clear=True, debug=[]):
        '''
        Make predictions
        f: file name for prediction
        '''
        arr = self.array_for_pred(f)
        res = self.curr_mod.predict(arr)      # prediction for segmentation
        if event:
            if 1 in debug:
                print(f' type(self.ev_mod) is {type(self.ev_mod)} ')
            res_ev = self.ev_mod.predict(arr)     # prediction event model
        ####
        if clear:
            tfk.backend.clear_session()     # avoid freezing
        if event:
            # save pred BF and pred event to mda_temp folder
            self.save_pred(f, res[0]*255, res_ev[0]*255)
        else:
            self.save_pred(f, res[0]*255)    # save pred to mda_temp folder

    def predict_mda(self, f):
        '''
        Prediction during mda
        '''
        self.predict_basic(f)

    def predict_live(self, track_live=False):
        '''
        Prediction during live session, real time predictions
        '''
        f = 'frame0.tiff'
        self.num_acq += 1           # current acq number
        self.addr_img_BF = opj(self.dir_pred, f[:-5] + '.png')
        self.predict_basic(f)
        if track_live:                      # tracking live
            try:
                if self.num_acq % self.freq_track == 0:
                    self.cam_track_BF()        # track the cells in live mode
            except:
                print('Cannot track live..')
        self.save_nb_cells()              # save the nb of cells in a yaml

    def predict_and_save(self, f=None, debug=[]):
        '''
        Make prediction and save for BF images
        '''
        if 1 in debug:
            print('#### in predict_and_save')
            print(f"f is {f}")
        if self.mode == 'mda':
            # find format framexx.tiff
            if re.findall('frame\\d+_t\\d+.tiff', f):
                self.predict_mda(f)     # predict during mda
        elif self.mode == 'live':
            self.predict_live()         # predict during live
