'''

'''
import os
from pathlib import Path
import glob
import copy
import cv2
from PIL import Image
from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np
from scipy.optimize import linear_sum_assignment
from scipy.linalg import norm
from skimage.filters import gaussian
from skimage.segmentation import active_contour
from skimage.segmentation import chan_vese
from skimage.restoration import denoise_tv_chambolle
from colorama import Fore, Back, Style
from modules.track_segm.events import EVENTS as EV
from modules.track_segm.track_methods import TRACK_METH as TM

class TRACK_SEGM(EV,TM):
    '''
    Tracking and Segmentation
    '''

    def __init__(self):
        '''
        '''
        EV.__init__(self)
        TM.__init__(self)
        self.dil_pred = 22              # dilate mask for each shape prediction
        # Tracking
        self.min_dist_change = 20       # minimum for change of distance
        self.iou_score_low_lim = 0.3    # inter over union score low limit
        self.list_prev_pos = []         # empty at the beginning
        self.random_colors()

    def random_colors(self):
        '''
        create random colors
        '''
        min_col = 0
        self.rand_col = [tuple(map(int,np.random.randint(min_col,255,3)))
                            for i in range(2000)]  # random color for tracking

    def circle_at_pos(self, pos, radius=10):
        '''
        '''
        try:
            # draw a circle around the center..
            self.img = cv2.circle(self.img, pos, radius, (255, 0, 0), 2)
        except:
            pass

    def fit_ellipse(self,c):
        '''
        Make the list of ellipses
        '''
        try:
            ell = cv2.fitEllipse(c)
            self.list_ellipses.append(ell)
        except:
            self.list_ellipses.append('a')

    def fill_list_pos(self, c, show_pos=False, debug=[]):
        '''
        Make the list of positions
        '''
        if 1 in debug:
            print(f'type(c) is {type(c)}')
        x, y, w, h = cv2.boundingRect(c)
        pos = (int(x + w/2), int(y + h/2))  # find position
        self.list_pos.append(pos)
        if show_pos:
            self.circle_at_pos(pos)

    def fill_list_pos_events(self, c, show_pos=False):
        '''
        Make the list of positions
        '''
        x, y, w, h = cv2.boundingRect(c)
        pos = (int(x + w/2), int(y + h/2))
        self.list_pos_events.append(pos)
        if show_pos:
            self.circle_at_pos(pos)

    def find_position_from_contour(self, all_cntrs, debug=[1]):
        '''
        For each cell prediction, find the position
        from the bounding box rectangle
        '''
        contours, contours_events = all_cntrs
        if 1 in debug:
            print(f'len(contours) is {len(contours)} ')
            try:
                print(f'len(contours_events) is {len(contours_events)} ')
            except:
                print('No contours_events')
        self.list_pos = []
        self.list_ellipses = []
        self.curr_contours = self.all_cntrs[self.num_acq] = contours
        for c in contours:
            # create the list of positions
            self.fill_list_pos(c)
            self.fit_ellipse(c)
        if contours_events:
            self.list_pos_events = []
            self.curr_contours_events =\
                self.all_cntrs_events[self.num_acq] = contours_events
            for c in contours_events:
                # create the list of events positions
                self.fill_list_pos_events(c)

    def get_radius(self,i):
        '''
        Equivalent radius for contour i
        '''
        area = cv2.contourArea(self.dic_dilated_contours[i])
        radius = np.sqrt(area/np.pi)
        return radius

    def radii_ij(self,i,j):
        '''
        Return the equivalent radii of i and j
        '''
        radiusi, radiusj = self.get_radius(i), self.get_radius(j)
        return radiusi, radiusj

    def dist_ij(self,i,j):
        '''
        Return the distance between i and j
        '''
        #posi, posj = self.list_prev_pos[i], self.list_prev_pos[j]
        posi, posj = self.list_pos[i], self.list_pos[j]
        distij = norm(np.array(posj) - np.array(posi))
        return distij

    def debug_add_neightbours(self,i,j):
        '''
        '''
        if j == 21 and i == 20:
            print("i ", i)
            print("j ", j)
            print('### sum_radii ', sum_radii)
            print('### distij ', distij)

    def add_neighbours(self, i, j, debug=0):
        '''
        add neighbours to self.dic_neighbours
        '''
        distij = self.dist_ij(i,j)
        radiusi, radiusj = self.radii_ij(i,j)
        sum_radii = radiusi + radiusj
        if debug > 0:
            self.debug_add_neightbours(i,j)
        if sum_radii > distij:
            self.dic_neighbours[i] += [j]                # add neighbour to i
            self.dic_neighbours[j] += [i]                # add neighbour to j

    def draw_neighbours(self,i, debug=[]):
        '''
        Draw a circle on the neighbours of contour i and on contour i
        '''
        self.img = cv2.circle(self.img, self.list_prev_pos[i],
                                            5, self.rand_col[i], -1)
        if 1 in debug:
            print('self.dic_neighbours ', self.dic_neighbours)
            print("### self.dic_neighbours[i] ", self.dic_neighbours[i])
        for j in self.dic_neighbours[i]:
            self.img = cv2.circle(self.img, self.list_prev_pos[j],
                                                3, self.rand_col[i], 2)

    def find_neighbours(self):
        '''
        Find the neighbours for each cell using the contour
        '''
        self.dic_neighbours = {i:[] for i in range(len(self.list_pos))}
        for i, posi in enumerate(self.list_pos):
            for j in range(i+1, len(self.list_pos)):
                self.add_neighbours(i,j)

    def swap_contours(self,i,ind):
        '''
        Change the index of the contour
        '''
        buff = self.curr_contours[i]
        self.curr_contours[i] = self.curr_contours[ind]
        self.curr_contours[ind] = buff

    def swap_positions(self, i, ind):
        '''
        Change the index of the pos
        '''
        buff = self.list_pos[i]
        self.list_pos[i] = self.list_pos[ind]
        self.list_pos[ind] = buff

    def make_swaps(self, i, ind, debug=[]):
        '''
        Swap the positions and the mask
        '''
        #print('list_distances[ind] is ', list_distances[ind])
        if i not in self.list_indices_pos:
            if 1 in debug:
                print(Fore.RED + Style.NORMAL +\
                   f'swapping ### i: {i} and ind: {ind} ')
                print(Style.RESET_ALL)
            self.swap_positions(i,ind)
            # refresh the index of the contour previously indexed i
            self.swap_contours(i,ind)
            # block position i
            self.list_indices_pos.append(i)
        if 1 in debug:
            print(Fore.BLUE + str(self.list_indices_pos))

    def dilate_mask(self, mask, dil=1, iter_dil=1):
        '''
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (dil, dil))
        mask = cv2.dilate(mask, kernel, iterations=iter_dil)    # dilate
        return mask

    def make_mask_from_contour(self,cnt, dilate=False, iter_dilate=1):
        '''
        Used in method 2 (predictions)
        '''

        h, w, nchan = self.img.shape
        mask = np.zeros((h, w), np.uint8 )
        cv2.drawContours(mask, [cnt], -1, (255, 255, 255), -1) # fill contour
        if dilate:
            mask = self.dilate_mask(mask, dil=dilate, iter_dil=iter_dilate)
        return mask

    def compare_areas(self, i, ind):
        '''
        Compare areas of the contours i and ind
        '''
        # previous contour i
        area0 = cv2.contourArea(self.all_cntrs[self.num_acq-1][i])
        # contour ind in new list
        area1 = cv2.contourArea(self.curr_contours[ind])
        ratio_areas = area0/area1

        return ratio_areas

    def IoU_filter(self,i,ind, debug=[]):
        '''
        Compare Intersection over Union..
        '''
        # previous contour
        mask0 = self.make_mask_from_contour(self.all_cntrs[self.num_acq-1][i])
        # new contour..
        mask1 = self.make_mask_from_contour(self.curr_contours[ind])
        inter = np.logical_and(mask0, mask1)
        union = np.logical_or(mask0, mask1)
        iou_score = np.sum(inter) / np.sum(union)
        if 1 in debug:
            print(f"### IoU score for {i} with {ind} is {iou_score}  ")
        return iou_score

    def changing_tests(self, i, ind, debug=[]):
        '''
        '''
        # comparing intersection over union
        iou_score = self.IoU_filter(i, ind)
        if iou_score < self.iou_score_low_lim:
            if 1 in debug:
                print(Fore.YELLOW + Style.NORMAL +
                 f'#### Huge difference between {i} and {ind} !!!! ')
                print(Style.RESET_ALL)
        # compare the areas of the contours
        ratio_areas = self.compare_areas(i, ind)
        if 0.7 < ratio_areas < 1.5:
            if 1 in debug:
                print(Fore.YELLOW + Style.NORMAL +
                 f'#### size ratio between {i} and {ind} is normal')
                print(Style.RESET_ALL)
        else:
            if 1 in debug:
                diff = f'from {i} to {ind} by factor {ratio_areas} '
                if ratio_areas < 1:
                    print(Fore.RED + Style.NORMAL +
                            '#### size increased ' + diff)
                else:
                    print(Fore.RED + Style.NORMAL +
                            '#### size decreased ' + diff)
                print(Style.RESET_ALL)

    def find_nearest_index_track(self, i):
        '''
        Index in the old position list of the nearest position
         of index i in the new position list
        '''

        return self.find_nearest_index(i, self.list_prev_pos)

    def radius_times_crit(self, i, ind, nbradius=2):
        '''
        Radius times criterion
        '''
        # contour of previous picture
        cnt0 = self.all_cntrs[self.num_acq-1][i]
        # radius of the original contour
        r0 = np.sqrt(cv2.contourArea(cnt0)/np.pi)
        # new distance must be less than 2 times the radius..
        return self.list_distances[ind] < nbradius*r0

    def change_with_nearest(self, i, dist_max=False, debug=[]):
        '''
        Change the position and the contours with the nearest elemt from i ..
        '''
        if 1 in debug: print('dealing with ', i)
        # index of the nearest contour from i
        ind = self.find_nearest_index_track(i)
        # detect if change is normal or not
        self.changing_tests(i, ind)
        if dist_max:
            # new distance must be less than 2 times the radius..
            if self.radius_times_crit(i, ind):
                # swap both masks and positions
                self.make_swaps(i, ind)
        else:
            self.make_swaps(i, ind)

    def show_new_positions(self):
        '''
        '''
        for i in range(len(self.list_pos)):
            if i not in self.list_indices_pos:
                self.img = cv2.circle(self.img,
                    self.list_pos[i], 5, (255, 255, 0), 1)

    def test_out_track_algo(self, old_pos, new_pos, debug=[]):
        '''
        '''
        ldiffnorm = []
        for i in range(min(len(old_pos), len(new_pos))):
            ldiffnorm += [round(norm(np.array(old_pos[i])
                                    -np.array(new_pos[i])), 1)]
        if 1 in debug:
            print(f'*****!!!!#### ldiffnorm {ldiffnorm}')

    def redefine_Id(self, meth='min'):
        '''
        Refresh each position with the nearest one..
        '''
        if meth == 'min':
            self.meth_min(self.list_prev_pos, self.list_pos, corr=True)
        elif meth == 'hung':
            self.meth_hung(self.list_prev_pos, self.list_pos, corr=True)

    def track_mess0(self):
        '''
        message 0
        '''

        print(Fore.GREEN + str(self.list_pos))
        print(len(self.list_pos))
        print(Style.RESET_ALL)

    def track_mess1(self):
        '''
        message 1
        '''

        print('##### saving old positions #####')
        print(Fore.YELLOW + str(self.list_prev_pos))
        print(len(self.list_prev_pos))
        print(Style.RESET_ALL)

    def plt_img(self, img):
        '''

        '''
        ##
        dpi_val = 100
        fig = plt.figure(figsize=(512/dpi_val, 512/dpi_val), dpi=dpi_val)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(img, aspect='equal', cmap='gray')

    def cell_tracking(self, num, all_cntrs, show_pos=False, debug=[]):
        '''
        Track the cells
        num : picture index
        all_cntrs : all contours extracted from current picture
        '''
        self.num_acq = num
        self.find_position_from_contour(all_cntrs)        # listpos
        if 1 in debug: self.track_mess0()
        if self.list_prev_pos:
            old_pos = copy.deepcopy(self.list_pos)
            self.redefine_Id(meth='min')                    #
            new_pos = copy.deepcopy(self.list_pos)
            self.test_out_track_algo(old_pos, new_pos)
            if show_pos:
                self.show_new_positions()
        self.find_indices_events()             # events like buds
        # ML method, method with ep5_v3 model
        self.cells_identification_simple()
        self.list_prev_pos = self.list_pos     # save positions for tracking
        if 2 in debug:
            self.track_mess1()      # list_prev_pos
        #print(Fore.BLUE +)

    def find_minmax_maxmean(self, new_img):
        '''
        '''
        new_img_vec = new_img.reshape(1, new_img.size)[0]  # from 2D to vector
        new_img_vec = new_img_vec[new_img_vec > 0]      # remove 0 values
        vec_sort = new_img_vec.argsort()                 # indices of sorted
        # max of the min values
        val_min_max = new_img_vec[vec_sort[:300]].max()
        # mean of max values
        val_max_mean = new_img_vec[vec_sort[::-1][:20]].mean()
        # difference between mean of max values and max of min values..
        diff = val_max_mean - val_min_max
        return val_min_max, val_max_mean, diff

    def largest_contour(self, contours):
        '''
        Largest contour
        '''
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]
        return cnt

    def masks_segmentation(self, i, cntr):
        '''
        Mask after segmentation
        '''
        self.dic_mask_seg[i] = np.zeros(self.img.shape)
        # save mask of the segmentation
        cv2.drawContours(self.dic_mask_seg[i], [cntr],
                                    -1, (255, 255, 255), -1)

    def denoising(self, kind='fastNlMeans'):
        '''
        Denoising for filling better
        '''
        for _ in range(int(self.args.nb_denoising)):
            if kind == 'fastNlMeans':
                self.img = cv2.fastNlMeansDenoising(self.img, None, 10, 7, 21)
            else:
                self.img = denoise_tv_chambolle(self.img, weight=0.03)

    def make_active_contour(self, contour):
        '''
        '''
        cntr = []
        cntr += [contour[:, 0][:, 0], contour[:, 0][:, 1]]
        cntr = np.array(cntr).T
        #print("#### cntr ", cntr)
        #try:
        # snake = active_contour(gaussian(self.img, 3),
        #            cntr, alpha=0.015, beta=10, gamma=0.001)
        snake = active_contour(gaussian(self.img, 1.1),
                   cntr, alpha=0.3, beta=10, gamma=0.001)
        snake = snake.astype('int')
        snake = np.array([[[s[0], s[1]]] for s in list(snake)])
        #except:
        #print('no snake..')
        # show the active contour
        cv2.drawContours(self.img, [snake], -1, (254, 0, 0), 1)
        cv2.drawContours(self.img, [contour], -1, (0, 254, 0), 1)

    def pos_ij(self, i, j):
        '''
        positions i and j in numpy array format
        '''
        posi = np.array(self.list_pos[i])
        posj = np.array(self.list_pos[j])
        return posi, posj

    def vec_ij(self, i, j):
        '''
        Vector from i to j
        '''
        posi, posj = self.pos_ij(i, j)
        vecij = posj-posi
        return vecij

    def norm_vec_ij(self, i, j):
        '''
        Vector from i to j
        '''
        posi, posj = self.pos_ij(i, j)
        vecij = posj-posi
        norm_vecij = vecij/norm(vecij)
        return norm_vecij

    def perp_vec_ij(self, i, j):
        '''
        Make the perpendicular unit vector
        '''
        # posi, posj = self.pos_ij(i,j)
        # vecij = posj-posi
        # norm_vecij = vecij/norm(vecij)
        norm_vecij = self.norm_vec_ij(i, j)
        perp_vecij = np.zeros(2)
        perp_vecij[0] = norm_vecij[1]
        perp_vecij[1] = -norm_vecij[0]
        return perp_vecij

    def barycenter_ij(self, i, j):
        '''
        Find the barycenter of the cells i an j according to their size
        '''
        radi, radj = self.radii_ij(i, j)
        posi, posj = self.pos_ij(i, j)
        baryc_ij = posi + radi/(radi+radj)*self.vec_ij(i, j)
        return baryc_ij

    def pos_num(self, i, shift=5):
        '''
        Position for the cell number in the picture
        '''
        pos = np.array(self.list_pos[i])
        if pos[1] < 500:
            pos += np.array([-shift, shift])
        return tuple(pos)

    def insert_num_cell(self, i, shift=5, img=None,
                        size=0.3, color=(255, 255, 255)):
        '''
        number of the cell for tracking
        '''
        font = cv2.FONT_HERSHEY_SIMPLEX
        pos = self.pos_num(i, shift=shift)
        if not (type(img) == np.ndarray):
            img = self.img
        if self.show_num_cell:             # show the cell number
            cv2.putText(img, str(i), pos, font, size, color, 1, cv2.LINE_AA)

    def debug_pos_i(self, pos, i):
        '''
        '''
        print(f'index is {i} ')
        print(f'pos is {pos} ')
        print(f'self.curr_contours {self.curr_contours[i]}')

    def fill_pred(self, i, mask):
        '''
        Fill prediction mask
        '''
        # color by thresholding with mask
        self.img[mask > 254] = self.rand_col[i]

    def color_num_cell(self, i, mask):
        '''
        '''
        self.fill_pred(i,mask)       # fill the prediction mask with color
        self.insert_num_cell(i)      # show the Id num of the cell

    def cells_identification_simple(self, debug=[]):
        '''
        Identify the cells
        '''
        list_pos = self.list_pos  # self.choose_list_pos()
        self.curr_mask = {}
        for i, pos in enumerate(list_pos):
            if 1 in debug:
                self.debug_pos_i(pos, i)
            if self.erode_after_pred:
                dil, iter_dil = self.dil_last_shape, self.iter_dil_last_shape
            else:
                dil, iter_dil = 1, 1
            # mask from contours with dilation
            mask = self.make_mask_from_contour(self.curr_contours[i],
                        dilate=dil, iter_dilate=iter_dil)
            if self.which_tracked != 'all':
                if i in self.which_tracked:
                    # color the cell and number it
                    self.color_num_cell(i, mask)
            else:
                self.color_num_cell(i, mask)
        self.insert_time_marks(self.img)
