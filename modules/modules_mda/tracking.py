import numpy as np
import cv2
from scipy.linalg import norm
from modules.track_segm.track_and_segment import TRACK_SEGM as TS
from modules.modules_mda.associated_tracking import ASSOCIATED_TRACKS as AT
from modules.util_server import find_platform, chose_server
from modules.util_misc import *

import pickle as pkl
from time import sleep
import shutil as sh

import os

op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

platf = find_platform()
server = chose_server(platf)


class TRACK(TS, AT):
    '''
    Tracking
    '''
    def __init__(self):
        '''
        Tracking
        '''
        lcls = [TS, AT]
        for cl in lcls:
            cl.__init__(self)
        # objective <--> displacement factor
        self.dic_displ_obj = {'10x': 1.560,
                              '20x': 0.780,
                              '40x': 0.390,
                              '60x': 0.260,
                              '100x': 0.156}
        self.index_track = -1

    def save_cntr_pkl(self, cntrs, name):
        '''
        Save the contours for further analysis
        '''
        with open(name, 'wb') as f_wb:
            pkl.dump(cntrs, f_wb)

    def track_BF(self, rep, use_corr=True, debug=[0]):
        '''
        Perform the tracking on the BF image
         and save the image of the tracked cells
        '''
        if 0 in debug:
            print(f'rep is {rep}')
        self.rep = rep
        self.img_cam = self.img.copy()
        if use_corr:
            try:
                # using correlation between images
                self.change_list_prev_pos()
            except:
                print('Cannot use correlation for tracking')
        else:
            if self.index_track == 0:
                # modify list_pos after centering
                self.change_list_prev_pos()
        # reinject the contours of the cells, None for events
        self.cell_tracking(rep, [self.curr_cntrs, None])
        name_pic = f'track_frame{self.num}_t{rep}.png'
        addr_pic = opj(self.dir_mda_temp, 'monitorings', 'tracking', name_pic)
        # save tracking
        cv2.imwrite(addr_pic, self.img)
        addr_cntrs = opj(self.dir_mda_temp,
                         'monitorings', 'tracking', 'all_cntrs.pkl')
        # pickle file for  the contours
        self.save_cntr_pkl(self.all_cntrs, addr_cntrs)

    def find_nearest_from_center(self):
        '''
        pos_center is the position of the cell
         the nearest from the center of the picture..
        '''
        # array of the new positions for BF
        arr_pos = np.array(self.list_pos)
        # all distances from position pos
        self.list_distances = list(map(norm,
                                       (arr_pos - np.array([256, 256]))))
        # find index of the closest new position..
        ind = np.argmin(self.list_distances)
        print(f'######## index of the cell'
              ' the nearest from the center is {ind} ')
        # position of the cell the nearest from the center
        self.pos_nearest_of_center = self.list_pos[ind]
        # index of the cell's position the nearest to the center
        self.index_pos_nearest_to_center = ind

    def find_translate(self, debug=[0]):
        '''
        Find the translation using correlation in the image
        '''
        img0 = cv2.imread(opj(self.dir_mda_temp,
                          f'frame{self.num}_t{self.rep - 1}.tiff'))
        img1 = cv2.imread(opj(self.dir_mda_temp,
                          f'frame{self.num}_t{self.rep }.tiff'))
        f0 = cv2.cvtColor(np.float32(img1), cv2.COLOR_BGR2GRAY)
        f1 = np.float32(cv2.cvtColor(np.float32(img0), cv2.COLOR_BGR2GRAY))
        shift = cv2.phaseCorrelate(f1, f0)
        if 0 in debug:
            print(f'Calculate the translation'
                  f' between images {self.rep-1} and {self.rep} ')
            print(f'For conserving the tracking, '
                  f'translation is {shift[0]} !!! ')

        return shift[0]

    def change_list_prev_pos(self, debug=[0]):
        '''
        Change list_pos values, for continuing the tracking with same Ids
        Continue, conserve the tracking
        '''
        dx, dy = self.find_translate()
        self.transl_with_corr = np.array([dx, dy])
        if 0 in debug:
            self.find_nearest_from_center()
            print(f'self.transl_with_corr is {self.transl_with_corr}')
        # changing reference list of positions
        self.list_prev_pos = list(np.array(self.list_pos) +
                                  self.transl_with_corr)
        self.find_nearest_from_center()
        if 0 in debug:
            print(f'self.chosen_numcell is {self.chosen_numcell}')
            print(f'self.list_prev_pos[self.chosen_numcell] '
                  f' = {self.list_prev_pos[self.chosen_numcell]}')

    def calc_dxdy_to_center_um(self, xy_img):
        '''
        From picture coordinates to displacement vector to the center in µm
        '''
        # dist to center in x in µm
        dx = self.fact_micro*(256 - xy_img[0])
        # dist to center in y in µm
        dy = self.fact_micro*(xy_img[1] - 256)
        print(f'### relative motion x,y in 512x512 pic : {dx,dy} µm')
        print(f'changed x,y for position')

        return dx,dy                  # displacement in µm

    def ask_for_xy(self):
        '''
        '''
        sleep(0.1)
        x_abs = self.pr.ask_pos('x')
        sleep(0.1)
        y_abs = self.pr.ask_pos('y')

        return x_abs, y_abs

    def eval_conditions_inside(self, x_abs, y_abs):
        '''
        '''
        # max distance between current coordinate and first coordinate
        dist_max = 300
        cnd0 = abs(x_abs - self.x0) > dist_max
        cnd1 = abs(y_abs - self.y0) > dist_max
        print(f'cnd0 is {cnd0} and cnd1 is {cnd1} ')    # conditions 0 and 1

        return cnd0, cnd1

    def ask_pos_inside(self, debug=[]):
        '''
        retrieve x and y staying inside the chamber (300µmx300µm)
        '''
        x_abs, y_abs = self.ask_for_xy()
        cnd0, cnd1 = self.eval_conditions_inside(x_abs, y_abs)
        while cnd0 or cnd1:
            # stay inside the cell
            x_abs, y_abs = self.ask_for_xy()
            cnd0, cnd1 = self.eval_conditions_inside(x_abs, y_abs)
            print(f'In ask_pos_inside, x_abs, y_abs = {x_abs, y_abs} ')

        return x_abs, y_abs

    def make_relative_move(self, dx, dy, debug=[]):
        '''
        Relative move for tracking
        '''
        if 0 in debug:
            print(f'dx,dy')
        # small correction for centering the cell
        self.pr.relative_move_to(dx, dy)
        # x, y positions
        x_abs, y_abs = self.ask_pos_inside()
        z_abs = self.ol.ask_zpos()                # z position
        print(f'x_abs, y_abs, z_abs positions are  {x_abs, y_abs, z_abs} ')
        print('used in list_steps')
        # change the current position
        self.list_steps['posxyz'].val = [x_abs, y_abs, z_abs]
        if 1 in debug:
            self.find_nearest_from_center()

    def find_pos_event(self, list_events_cells,
                       kind_choice='random', debug=[]):
        '''
        Find the absolute position of the event (bud, mating etc..)
        Take randomly an envent in the list
        '''
        if kind_choice == 'random':
            ind = np.random.randint(len(list_events_cells))
        elif kind_choice == 'lowest':
            # do not take at random, take the lowest
            ind = 0
        self.chosen_numcell = list_events_cells[ind]
        if 0 in debug:
            print(f'chosen index'
                  f'ind = {ind} i.e cell num {self.chosen_numcell} ')
        # index 0 of cells with fluorescence
        cell_chosen = list_events_cells[ind]
        # position of the cell to be tracked, taking the first index
        pos_event = self.list_pos[cell_chosen]
        if 2 in debug:
            print(f'pos_event is {pos_event}')
        try:
            # show in the BF image which event retained
            self.superimpose_event(cell_chosen)
        except:
            print('Cannot superimpose contour')
        print(f'############# will displace observed object to the center !!!')
        return pos_event

    def copy_suppl_monitorings_in_event_folder(self, event_pics, event_index):
        '''
        '''
        addr_pred_event = opj(self.dir_mda_temp,
                              'monitorings', 'pred',
                              f'pred_ev_frame{self.num}_t{self.rep}.png')
        try:
            sh.copy(addr_pred_event, event_pics)
        except:
            print('Cannot copy, prediction probably does not exist !!!..')
        addr_hist_event = opj(self.dir_mda_temp, 'monitorings',
                              'tracking',
                              f'buds{event_index}_history_pos{self.num}.png')
        try:
            sh.copy(addr_hist_event, event_pics)
        except:
            print('Cannot copy, history probably does not exist !!!..')

    def superimpose_event(self, event_index):
        '''
        Show which event was selected by drawing
        the event contour in the BF image
        Red contour around the cell..
        '''
        mask, dil_cntr = self.dilate_contour(event_index,
                                             dil=4, draw_dilated=False)
        img_BF = cv2.imread(opj(self.dir_mda_temp,
                                f'frame{self.num}_t{self.rep}.tiff'))
        # cell event contour
        img_event = cv2.drawContours(img_BF, [dil_cntr], -1, (0, 0, 254), 1)
        # insert num cell event
        self.insert_num_cell(event_index, shift=10,
                             img=img_BF, color=(0, 255, 0))
        self.insert_time_marks(img_BF)             # insert the time
        name_pic = f'triggering_event{self.num}_t{self.rep}.tiff'
        # folder for pictures events
        event_pics = opj(self.dir_mda_temp, 'monitorings', 'events')
        addr_pic = opj(event_pics, name_pic)
        cv2.imwrite(addr_pic, img_event)
        self.copy_suppl_monitorings_in_event_folder(event_pics, event_index)

    def centering(self, pos, debug=[]):
        '''
        Center the objective on the event
        '''
        if 0 in debug:
            print(f'self.chosen_numcell is {self.chosen_numcell}')
            print(f'self.list_prev_pos[self.chosen_numcell]'
                  f' before = {self.list_prev_pos[self.chosen_numcell]}')
        # difference between nearest cell and the center
        dx, dy = self.calc_dxdy_to_center_um(pos)
        # keep the position on the event at the center
        self.make_relative_move(dx, dy)

    def track_on_event(self, list_events_cells, debug=[1, 2, 3]):
        '''
        list_events_cells : indices where happened the event
        find_pos_event : return the position of the event
        '''
        if 1 in debug:
            print(f'list_events_cells {list_events_cells} '
                  ' (list of the events indices)')
            print(f'pos.tracking {self.tracking}')

        # center and track, waiting for an event

        # detected an event, tracking was inactive
        if list_events_cells and not self.tracking:
            if 2 in debug:
                print(f'event found, found event, '
                      f' event detected at iteration {self.rep}')
                print(f'list_events_cells {list_events_cells} '
                      ' (list of the events indices)')
            # find the position in absolute coordinates of the event
            pos_event = self.find_pos_event(list_events_cells)
            # center the first event
            self.centering(pos_event)
            # counting the number of events tracked since the beginning
            self.nb_tracks += 1
            # position in the current tracking
            self.index_track = 0
            if 3 in debug:
                # nb of cells which have been tracked..
                print(f'self.nb_tracks is  {self.nb_tracks}')
            self.tracking = True

        # keep tracking the event detected

        elif self.tracking:             # tracking
            print(f'############# keep the cell at the center !!!')
            # keep the position on the event at the center
            self.centering(self.pos_nearest_of_center)
            self.index_track += 1
        else:
            print('no event detected yet')
