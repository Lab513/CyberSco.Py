'''
py detect_cells.py -f '/home/meglio/Bureau/boulot/cells_videos/BF_f0000.tif'  -m  ep5_dil3_fl  --track all
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
from events import EVENTS as EV
from track_methods import TRACK_METH as TM

class TRACK_SEGM(EV,TM):
    '''
    Tracking and Segmentation
    '''

    def __init__(self):
        '''
        '''
        EV.__init__(self)
        TM.__init__(self)
        # Floodfill method
        self.dil_pred = 22                     # dilate mask for each shape prediction
        self.fl_d = 10                         # floodfill down
        self.fl_u = 16                         # floodfill up, used in adaptive
        self.lim_sup_seeds = 40                # val max for creating a seed
        self.thick_frontier = 20               # thickness for correction around the frontiers between cells
        self.seed_floodfill_bckgd = (10,10)    # position of the seed for finding the background
        self.dil_mask_bckgrd = 4               # dilation for the background mask
        self.nb_test_seeds = 200               # nb of random seed tested for the making the mask with the background..
        # Tracking
        self.min_dist_change = 20              # minimum for change of distance
        self.iou_score_low_lim = 0.3           # inter over union score low limit
        self.list_prev_pos = []                # empty at the beginning

    def random_colors(self):
        '''
        create random colors
        '''
        min_col = 254 if self.args.one_color else 0
        self.rand_col = [tuple(map(int,np.random.randint(min_col,255,3))) for i in range(2000)]  # random color for tracking

    def circle_at_pos(self, pos, radius=10):
        '''
        '''
        try:
            #self.img_mask = cv2.circle(self.img_mask, pos, radius, (255, 0, 0), 2) # draw a circle around the center..
            self.img = cv2.circle(self.img, pos, radius, (255, 0, 0), 2) # draw a circle around the center..
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

    def fill_list_pos(self, c, show_pos=False):
        '''
        Make the list of positions
        '''
        x, y, w, h = cv2.boundingRect(c)
        pos = ( int(x + w/2), int(y + h/2) ) # find position
        self.list_pos.append(pos)
        if show_pos:
            self.circle_at_pos(pos)

    def fill_list_pos_events(self, c, show_pos=False):
        '''
        Make the list of positions
        '''
        x, y, w, h = cv2.boundingRect(c)
        pos = ( int(x + w/2), int(y + h/2) )
        self.list_pos_events.append(pos)
        if show_pos:
            self.circle_at_pos(pos)

    def find_position_from_contour(self, all_cntrs):
        '''
        For each cell prediction, find the position from the bounding rectangle
        '''
        contours, contours_events = all_cntrs
        self.list_pos = []
        self.list_ellipses = []
        self.curr_contours = self.contours[self.num] = contours
        for c in contours:
            self.fill_list_pos(c)                         # create the list of positions
            self.fit_ellipse(c)
        if contours_events:
            self.list_pos_events = []
            self.curr_contours_events = self.contours_events[self.num] = contours_events
            for c in contours_events:
                self.fill_list_pos_events(c)                # create the list of events positions

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
        distij = norm( np.array(posj) - np.array(posi) )
        return distij

    def debug_add_neightbours(self,i,j):
        '''
        '''
        if j == 21 and i == 20:
            print("i ",i)
            print("j ",j)
            print('### sum_radii ', sum_radii)
            print('### distij ', distij)

    def add_neighbours(self,i,j,debug=0):
        '''
        add neighbours to self.dic_neighbours
        '''
        distij = self.dist_ij(i,j)
        radiusi, radiusj = self.radii_ij(i,j)
        sum_radii = radiusi + radiusj
        if debug > 0 : self.debug_add_neightbours(i,j)
        if sum_radii > distij:
            self.dic_neighbours[i] += [j]    # add neighbour to i
            self.dic_neighbours[j] += [i]    # add neighbour to j

    def draw_neighbours(self,i):
        '''
        Draw a circle on the neighbours of contour i and on contour i
        '''
        self.img = cv2.circle(self.img, self.list_prev_pos[i], 5, self.rand_col[i], -1)
        print('self.dic_neighbours ', self.dic_neighbours)
        print("### self.dic_neighbours[i] ", self.dic_neighbours[i])
        for j in self.dic_neighbours[i]:
            self.img = cv2.circle(self.img, self.list_prev_pos[j], 3, self.rand_col[i], 2)

    def find_neighbours(self):
        '''
        Find the neighbours for each cell using the masks contour
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

    def swap_positions(self,i,ind):
        '''
        Change the index of the pos
        '''
        buff = self.list_pos[i]
        self.list_pos[i] = self.list_pos[ind]
        self.list_pos[ind] = buff

    def make_swaps(self,i,ind):
        '''
        Swap the positions and the mask
        '''
        #print('list_distances[ind] is ', list_distances[ind])
        if i not in self.list_indices_pos:
            print(Fore.RED + Style.NORMAL + 'swapping ### i: {0} and ind: {1} '.format(i,ind))
            print(Style.RESET_ALL)
            self.swap_positions(i,ind)
            self.swap_contours(i,ind)                                           # refresh the index of the contour previously indexed i
            self.list_indices_pos.append(i)                                     # block position i
        print(Fore.BLUE + str(self.list_indices_pos))

    def dilate_mask(self, mask, dil=1, iter_dil=1):
        '''
        '''
        kernel = cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (dil,dil) )
        mask = cv2.dilate( mask, kernel, iterations = iter_dil )    # dilate
        return mask

    def make_mask_from_contour(self,cnt, dilate=False, iter_dilate=1):
        '''
        Used in method 2 (predictions)
        '''

        h, w, nchan = self.img.shape
        mask = np.zeros( ( h, w ), np.uint8  )
        cv2.drawContours( mask, [cnt], -1, (255, 255, 255), -1 ) # fill contour
        if dilate:
            mask = self.dilate_mask(mask, dil=dilate, iter_dil=iter_dilate)
        return mask

    def compare_areas(self,i,ind):
        '''
        Compare areas of the contours i and ind
        '''

        area0 = cv2.contourArea( self.contours[self.num-1][i] )  # previous contour i
        area1 = cv2.contourArea( self.curr_contours[ind] )       # contour ind in new list
        ratio_areas = area0/area1

        return ratio_areas

    def IoU_filter(self,i,ind):
        '''
        Compare Intersection over Union..
        '''

        mask0 = self.make_mask_from_contour( self.contours[self.num-1][i] )                      # previous contour
        mask1 = self.make_mask_from_contour( self.curr_contours[ind] )                           # new contour..
        inter = np.logical_and( mask0, mask1 )
        union = np.logical_or( mask0, mask1 )
        iou_score = np.sum(inter) / np.sum(union)
        print("### IoU score for {0} with {1} is {2}  ".format( i, ind, iou_score ))
        return iou_score

            #radius = 15
            #self.img = cv2.circle( self.img, self.list_pos[ind], radius, (255,)*3, 1 )
            # size = 15
            # vsize = np.array([size,size])
            # beg = np.array(self.list_pos[ind]) - vsize
            # end = beg + 2*vsize
            # self.img = cv2.rectangle(self.img, beg, end, (255,255,255), -1)
        #area = cv2.contourArea( self.curr_contours[i] )

    def changing_tests(self,i,ind):
        '''
        '''

        iou_score = self.IoU_filter( i,ind )                               # comparing intersection over union
        if iou_score < self.iou_score_low_lim:
            print(Fore.YELLOW + Style.NORMAL + '#### Huge difference between {0} and {1} !!!! '.format(i,ind))
            print(Style.RESET_ALL)
        ratio_areas = self.compare_areas( i,ind )                  # compare the areas of the contours
        if 0.7 < ratio_areas < 1.5:
            print(Fore.YELLOW + Style.NORMAL + '#### size ratio between {0} and {1} is normal'.format(i,ind))
            print(Style.RESET_ALL)
        else :
            diff = 'from {0} to {1} by factor {2} '.format( i, ind, ratio_areas )
            if ratio_areas < 1:
                print( Fore.RED + Style.NORMAL + '#### size increased ' + diff )
            else:
                print( Fore.RED + Style.NORMAL + '#### size decreased ' + diff )
            print(Style.RESET_ALL)

    # def find_nearest_index(self,i, comp_list):
    #     '''
    #     Index in the old position list of the nearest position of index i in the new position list
    #     '''
    #
    #     arr_pos = np.array(self.list_pos)                                              # array of the new positions
    #     pos = comp_list[i]                                                    # previous position
    #     self.list_distances = list( map( norm, ( arr_pos - np.array(pos) ) ) )         # all distances from position pos
    #     ind = np.argmin( self.list_distances )                                         # find index of the closest new position..
    #     print('arr_pos[ind] {0}, pos {1}'.format( arr_pos[ind], pos ))
    #
    #     return ind

    def find_nearest_index_track(self,i):
        '''
        Index in the old position list of the nearest position of index i in the new position list
        '''

        return self.find_nearest_index(i, self.list_prev_pos)

    def radius_times_crit(self, i, ind, nbradius=2):
        '''
        Radius times criterion
        '''
        cnt0 = self.contours[self.num-1][i]                      # contour of previous picture
        r0 = np.sqrt(cv2.contourArea( cnt0 )/np.pi)              # radius of the original contour
        return self.list_distances[ind] < nbradius*r0            # new distance must be less than 2 times the radius..

    def change_with_nearest(self, i, dist_max=False):
        '''
        Change the position and the contours with the nearest elemt from i ..
        '''
        print('dealing with ', i)
        ind = self.find_nearest_index_track(i)           # index of the nearest contour from i
        self.changing_tests( i,ind )                     # detect if change is normal or not
        if dist_max:
            if self.radius_times_crit(i, ind):           # new distance must be less than 2 times the radius..
                self.make_swaps( i,ind )                 # swap both masks and positions
        else:
            self.make_swaps( i,ind )

    def show_new_positions(self):
        '''
        '''
        for i in range(len(self.list_pos)):
            if i not in self.list_indices_pos:
                self.img = cv2.circle(self.img, self.list_pos[i], 5, (255,255,0), 1)

    def test_out_track_algo(self, old_pos, new_pos):
        '''
        '''
        ldiffnorm = []
        for i in range(min(len(old_pos),len(new_pos))):
            ldiffnorm += [round(norm(np.array(old_pos[i])-np.array(new_pos[i])),1)]
        print(f'*****!!!!#### ldiffnorm {ldiffnorm}')

    def redefine_Id(self, meth='min'):
        '''
        Refresh each position with the nearest one..
        '''
        if meth == 'min':
            self.meth_min(self.list_prev_pos, self.list_pos, corr=True)
        elif meth == 'hung':
            self.meth_hung(self.list_prev_pos, self.list_pos, corr=True)

        # self.list_indices_pos = []                 # list of indices for preventing moving yet moved indices..
        # for i in range(len(self.list_prev_pos)):
        #     #self.change_with_nearest(i)
        #     try:
        #         self.change_with_nearest(i)
        #     except:
        #         print('problem with change position for {0} '.format(i))

    # def make_hungarian_matrix(self, lp1, lp2):
    #     '''
    #     '''
    #     mat = []
    #     for j,p1 in enumerate(lp1):
    #         mat += [[]]
    #         for p2 in lp2:
    #             mat[j] += [norm(p2-p1)**2]
    #     return mat

    # def redefine_Id(self):
    #     '''
    #     Hungarian
    #     '''
    #
    #     lp1 = [ np.array(list(p1)) for p1 in self.list_prev_pos]
    #     lp2 = [ np.array(list(p2)) for p2 in self.list_pos]
    #     mat = self.make_hungarian_matrix(lp1, lp2)
    #     row_ind, col_ind = linear_sum_assignment(mat)
    #     # buffer dics
    #     dic_pos_interm = {}
    #     dic_cntr_interm = {}
    #     print(f"### After hungarian algo, the new order is {col_ind}")
    #     for j,ind in enumerate(col_ind):
    #         print(f"### j,ind is {j,ind}")
    #         if j != ind:
    #             if j in dic_pos_interm.keys():
    #                 print(f"take from buffer {j}")
    #                 self.list_pos[ind] = dic_pos_interm[j] # use the buffer
    #                 self.curr_contours[ind] = dic_cntr_interm[j]
    #                 dic_pos_interm.pop(j)                # remove from buffer
    #                 dic_cntr_interm.pop(j)
    #             else:
    #                 print(f"keep in buffer {j}")
    #                 dic_pos_interm[ind] = self.list_pos[ind]           # keep in the buffer
    #                 dic_cntr_interm[ind] = self.curr_contours[ind]     # keep in the buffer
    #         self.list_pos[ind] = self.list_pos[j]
    #         self.curr_contours[ind] = self.curr_contours[j]
    #     if len(dic_pos_interm) > 0 :                                # keep the new values
    #         for k in dic_pos_interm.keys():
    #             print(f"empty from buffer {k}")
    #             self.list_pos.append(dic_pos_interm[k])
    #             self.curr_contours.append(dic_cntr_interm[k])

    # def redefine_Id(self):
    #     '''
    #     Hung
    #     '''
    #
    #     lp1 = [ np.array(list(p1)) for p1 in self.list_prev_pos]
    #     lp2 = [ np.array(list(p2)) for p2 in self.list_pos]
    #     mat = self.make_hungarian_matrix(lp1, lp2)
    #     row_ind, col_ind = linear_sum_assignment(mat)
    #     print(f"### After hungarian algo, the new order is {col_ind}")
    #     lprev = len(col_ind)
    #     print(f"### lprev is {lprev}")
    #     list_pos_interm = [0]*lprev
    #     list_cntrs_interm = [0]*lprev
    #     for j,ind in enumerate(col_ind):
    #         print(f"### j,ind is {j,ind}")
    #         list_pos_interm[j] = self.list_pos[ind]
    #         list_cntrs_interm[j] = self.curr_contours[ind]
    #     print(f'list_pos_interm = {list_pos_interm}')
    #     for i,p in enumerate(list_pos_interm):
    #         if p !=0:
    #             self.list_pos[i] = p
    #     for i,c in enumerate(list_cntrs_interm):
    #         if c !=0:
    #             self.curr_contours[i] = c

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

    def cell_tracking_and_segmentation(self, num, all_cntrs, show_pos=False):
        '''
        Track the cells
        '''
        self.num = num
        self.find_position_from_contour(all_cntrs) # listpos
        self.track_mess0()
        if self.list_prev_pos:
        #try:
            old_pos = copy.deepcopy(self.list_pos)
            self.redefine_Id(meth='min')                    # correction of the position after new contours
            new_pos = copy.deepcopy(self.list_pos)
            self.test_out_track_algo(old_pos, new_pos)
            if show_pos:
                self.show_new_positions()
        # except:
        #     print('cannot redefine Id')
        #     try:
        #         print(f'## len(self.list_prev_pos) is {len(self.list_prev_pos)}')
        #     except:
        #         print('A priori no self.list_prev_pos')
        self.find_indices_events()                        # events like buds
        if self.args.method == 1:
            self.cells_segmentation_with_floodfill()      # Floodfill method
        elif self.args.method == 2:                       #
            self.cells_identification_simple()            # ML method, method with ep5_v3 model
        self.list_prev_pos = self.list_pos                # save positions for tracking
        self.track_mess1()                                # list_prev_pos
        #print(Fore.BLUE + )

    def dilated_mask_built_on_contour(self,i):
        '''
        Used in method 1
        '''
        h, w, nchan = self.img.shape
        mask = np.zeros( ( h+2, w+2 ), np.uint8  )
        cv2.drawContours( mask, [self.curr_contours[i]], -1, (255, 255, 255), -1 ) # fill contour
        area = cv2.contourArea( self.curr_contours[i] )
        #newdil = int(self.dil_pred/3 + area/20)
        #print("## area", area)
        #kernel = np.ones( (dil,dil), np.uint8 )
        #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (newdil, newdil))
        kernel = cv2.getStructuringElement( cv2.MORPH_ELLIPSE, (self.dil_pred, self.dil_pred) )
        mask = cv2.dilate( mask, kernel, iterations = 1 )    # dilate
        return mask

    def dilate_contour(self, i, draw_dilated=True):
        '''
        '''
        mask = self.dilated_mask_built_on_contour(i)
        contour, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:] # refind contours
        mask = cv2.bitwise_not(mask)
        if self.args.dil_cntrs:                        # show the dilated contour in image
            cv2.drawContours( self.img, [contour[0]], -1, (254, 254, 254), 1 )
        return mask, contour[0]

    # def convexhull_maxpts(self, mask, max_seeds=100, debug=0):
    #     '''
    #     Find the seeds for floodFill in the "corona"
    #     '''
    #     new_img = self.img.copy()
    #
    #     new_img_vec = new_img.reshape(1, new_img.size)[0]
    #     new_img_vec = new_img_vec[ new_img_vec > 0 ]
    #     vec_sort = new_img_vec.argsort()
    #     val_max = new_img_vec[ vec_sort[::-1][:20] ]

    def find_minmax_maxmean(self, new_img):
        '''
        '''
        new_img_vec = new_img.reshape(1, new_img.size)[0]            # from 2D to vector
        new_img_vec = new_img_vec[ new_img_vec > 0 ]                 # remove 0 values
        vec_sort = new_img_vec.argsort()                             # indices of sorted
        val_min_max = new_img_vec[ vec_sort[:300] ].max()            # max of the min values
        val_max_mean = new_img_vec[ vec_sort[::-1][:20] ].mean()     # mean of max values
        diff = val_max_mean - val_min_max                            # difference between mean of max values and max of min values..
        return val_min_max, val_max_mean, diff

    def seeds_with_val_min_max(self, imup, val_min_max):
        '''
        '''
        loc = np.where( imup < val_min_max )
        pos_seeds = list(zip(loc[1][::3],loc[0][::3]))               # seeds
        return pos_seeds

    def debug_find_seeds_minval(self, val_max_mean, diff, val_min_max):
        '''
        '''
        print('#### val_max_mean ', val_max_mean)
        print('#### diff ', diff)
        print('#### val_min_max ', val_min_max)

    def find_seeds_minval(self, mask, max_seeds=100, debug=0):
        '''
        Find the seeds for floodFill in the "corona"
        '''
        new_img = self.img.copy()
        new_img[ mask[1:-1,1:-1] > 100 ] = (255,255,255)
        imup = new_img.copy()
        new_img[new_img == 255] = 0
        val_min_max, val_max_mean, diff = self.find_minmax_maxmean(new_img)
        pos_seeds = self.seeds_with_val_min_max(imup, val_min_max)
        ##
        if debug > 0:
            self.debug_find_seeds_minval(val_max_mean, diff, val_min_max)
        return pos_seeds, diff-20, val_min_max

    def largest_contour(self, contours):
        '''
        Largest contour
        '''
        areas = [cv2.contourArea(c) for c in contours]
        max_index = np.argmax(areas)
        cnt = contours[max_index]
        return cnt

    def find_floodfills_contour(self,i,limg, polydp=False):
        '''
        '''
        new_img = self.img.copy()
        new_img[:,:,:] = 0
        for j in range(3):
            for elem in limg:
                new_img[:,:,j][elem[:,:,j] == 255] = 255 #self.rand_col[i][j]
        ##
        imgray = cv2.cvtColor(new_img, cv2.COLOR_BGR2GRAY)
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        max_cnt = self.largest_contour(contours)
        if polydp:
            max_cnt = cv2.approxPolyDP(max_cnt, 0.03 * cv2.arcLength(max_cnt, True), True) # smoothing the contours with polynoms
        return max_cnt

    def masks_segmentation(self, i, cntr):
        '''
        Mask after segmentation
        '''
        self.dic_mask_seg[i] = np.zeros(self.img.shape)
        cv2.drawContours( self.dic_mask_seg[i], [cntr], -1, (255,255,255), -1 )  # save mask of the segmentation

    def floddfill_contour(self, i, limg, cntr_line=-1):
        '''
        Make the contour for the floodfilled region
        cntr_line=-1 : fill the contour
        '''
        cntr = self.find_floodfills_contour(i,limg)
        if self.args.dil_cntrs: cntr_line = 1
        cv2.drawContours( self.img, [cntr], -1, self.rand_col[i], cntr_line )  # show the active contour # self.rand_col[i]
        #print('drew contour ',i)
        self.masks_segmentation(i, cntr)
        self.dic_segm_area[i] = cv2.contourArea(cntr)                          # save cell's area

    def fill_cell(self, i, bounds='adaptive', make_circle=False):
        '''
        '''
        mask = self.dic_dil_cntrs_masks[i]
        try:
            pos = self.list_prev_pos[i]
            if make_circle:
                self.img = cv2.circle( self.img, pos, 5, (255,0,0), 1 )
        except:
            print('Probably an error with self.list_prev_pos[i]')
        pos_seeds, diff, val_min_max = self.find_seeds_minval(mask)
        #
        if bounds == 'fixed':
            lod, upd = (self.lim_sup_seeds,)*4, (self.fl_u,)*4   # fixed
        else:
            lod, upd = (int(val_min_max),)*4, (self.fl_u,)*4     # semi-adaptive
        limg = []
        for k,pos in enumerate( pos_seeds ):
            limg.append( self.img.copy() )
            cv2.floodFill( limg[k], mask, seedPoint=pos, newVal=(255,)*3, loDiff=lod, upDiff=upd )
        self.floddfill_contour( i, limg )

    def denoising(self, kind='fastNlMeans'):
        '''
        Denoising for filling better
        '''
        for i in range(int(self.args.nb_denoising)):
            if kind == 'fastNlMeans':
                self.img = cv2.fastNlMeansDenoising(self.img, None, 10, 7, 21)
            else:
                self.img = denoise_tv_chambolle(self.img, weight=0.03)

    def make_active_contour(self, contour):
        '''
        '''
        cntr = []
        cntr += [contour[:,0][:,0], contour[:,0][:,1]]
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
        cv2.drawContours( self.img, [snake], -1, (254,0,0), 1 )         # show the active contour
        cv2.drawContours( self.img, [contour], -1, (0, 254, 0), 1 )     #

    # def make_chanvese(self):
    #     '''
    #     '''
    #     cv = chan_vese(image, mu=0.25, lambda1=1, lambda2=1, tol=1e-3, max_iter=200,
    #            dt=0.5, init_level_set="checkerboard", extended_output=True)

    def pos_ij(self,i,j):
        '''
        positions i and j in numpy array format
        '''
        # posi = np.array(self.list_prev_pos[i])
        # posj = np.array(self.list_prev_pos[j])
        posi = np.array(self.list_pos[i])
        posj = np.array(self.list_pos[j])
        return posi, posj

    def vec_ij(self,i,j):
        '''
        Vector from i to j
        '''
        posi, posj = self.pos_ij(i,j)
        vecij = posj-posi
        return vecij

    def norm_vec_ij(self,i,j):
        '''
        Vector from i to j
        '''
        posi, posj = self.pos_ij(i,j)
        vecij = posj-posi
        norm_vecij = vecij/norm(vecij)
        return norm_vecij

    def perp_vec_ij(self,i,j):
        '''
        Make the perpendicular unit vector
        '''
        # posi, posj = self.pos_ij(i,j)
        # vecij = posj-posi
        # norm_vecij = vecij/norm(vecij)
        norm_vecij = self.norm_vec_ij(i,j)
        perp_vecij = np.zeros(2)
        perp_vecij[0] = norm_vecij[1]
        perp_vecij[1] = -norm_vecij[0]
        return perp_vecij

    def barycenter_ij(self,i,j):
        '''
        Find the barycenter of the cells i an j according to their size
        '''
        radi, radj = self.radii_ij(i,j)
        posi, posj = self.pos_ij(i,j)
        baryc_ij = posi + radi/(radi+radj)*self.vec_ij(i,j)
        return baryc_ij

    def beg_end_points_perp_mask(self,i,j):
        '''
        Make beginning and ending point for frontiers..
        '''
        baryc_ij = self.barycenter_ij(i,j) + self.norm_vec_ij(i,j)*self.thick_frontier/2
        begpt = baryc_ij - 10*self.perp_vec_ij(i,j)
        endpt = baryc_ij + 10*self.perp_vec_ij(i,j)
        endpt = tuple(endpt.astype('int'))
        begpt = tuple(begpt.astype('int'))
        return begpt, endpt

    def beg_end_points_perp_line(self,i,j):
        '''
        Make beginning and ending point for frontiers..
        '''
        baryc_ij = self.barycenter_ij(i,j)
        begpt = baryc_ij - 10*self.perp_vec_ij(i,j)
        endpt = baryc_ij + 10*self.perp_vec_ij(i,j)
        endpt = tuple(endpt.astype('int'))
        begpt = tuple(begpt.astype('int'))
        return begpt, endpt

    def plot_mask(self, mask, title=None):
        '''
        Plot mask individually
        '''
        plt.close('all')
        plt.figure()
        if title:
            plt.title(title)
        plt.imshow(mask)

    def show_frontiers(self,i,j):
        '''
        Show where are found the frontiers
        '''
        begpt, endpt = self.beg_end_points_perp_line(i,j)
        cv2.line(self.img, begpt, endpt, (0,255,255), thickness = 1)

    def make_frontier_mask(self,i,j,mask):
        '''
        Complete the mask with frontier information
        '''
        begpt, endpt = self.beg_end_points_perp_mask(i,j)
        cv2.line(mask, begpt, endpt, (255,255,255), thickness = self.thick_frontier) # correction on the mask

    def change_mask_with_neighbours(self, i, kind='mask', show_mask=False, debug=0):
        '''
        Make corrections on the mask or just show the frontiers
        '''
        mask = self.dic_dil_cntrs_masks[i]
        if show_mask : self.plot_mask(mask)
        try:
            for j in self.dic_neighbours[i]:
                if debug > 0:
                    print("endpt ", endpt)
                    print("begpt ", begpt)
                if kind == 'frontier' or self.args.frontiers:
                    self.show_frontiers(i,j)
                if kind == 'mask' :
                    self.make_frontier_mask(i,j,mask)
        except:
            #print('no neighbour')
            pass
        if kind == 'mask':
            self.dic_dil_cntrs_masks[i] = mask

    def dilate_mask_background(self, i, mask, show_mask=False):
        '''
        '''
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (self.dil_mask_bckgrd, self.dil_mask_bckgrd))
        mask = cv2.dilate(mask, kernel, iterations = 1)    # dilate bckgd and in the same time reduce each cell's mask size..
        if show_mask: self.plot_mask(mask, title='dilating')
        self.dic_dil_cntrs_masks[i] = mask

    def find_furthest_seed(self):
        '''
        Find the seed the furthest from all the cells positions
        '''
        arr_pos = np.array(self.list_pos)                                                                       # array of the new positions
        self.rand_pos = [tuple(map(int,np.random.randint(0,self.size,2))) for i in range(self.nb_test_seeds)]   # random positions in the pic
        print("#### self.rand_pos is ", self.rand_pos)
        currmax = 0
        maxi = 0
        for i,pos in enumerate(self.rand_pos):
            self.list_distances = list( map( norm, ( arr_pos - np.array(pos) ) ) )       #
            max_dist = min(self.list_distances)                                         #
            if max_dist > currmax:
                currmax = max_dist
                maxi = i
        return self.rand_pos[maxi] # furthest position

    def make_mask_bckgd(self, debug=0):
        '''
        Make the background mask for making correctly the segmentation.
        It uses the furthest seed from all the points from a pool of random seed proposed in the image.
        '''
        lod, upd = (8,)*4, (5,)*4
        self.bckgd = self.img.copy()
        self.furthest_seed = self.find_furthest_seed()                   # find a seed the further from all the points
        cv2.floodFill(self.bckgd, None, seedPoint=self.furthest_seed,\
                      newVal=(255,255,255) , loDiff=lod, upDiff=upd)

    def change_mask_with_bckgd(self, i, debug=0):
        '''
        Modify mask using background for avoiding floodfill to drool outside of the cells..
        '''
        mask = self.dic_dil_cntrs_masks[i]
        mask[ 1:-1, 1:-1 ][ self.bckgd[:,:,0] == 255 ] = 255  # use background in the mask
        ##
        self.dilate_mask_background(i, mask)

    def fill_image_bckgrd(self):
        '''
        Fill the background for visualizing how floodfill performs
        '''
        lod, upd = (8,)*4, (5,)*4
        cv2.floodFill(self.img, None, seedPoint=self.seed_floodfill_bckgd,\
                        newVal=(0,0,0) , loDiff=lod, upDiff=upd)

    def change_mask(self,i):
        '''
        Modify the mask for a better segmentation..
        '''
        self.change_mask_with_bckgd(i)               # modify the current mask with the background mask..
        #if self.args.use_frontiers:
        self.change_mask_with_neighbours(i)          # modify mask with frontiers with neighbours

    def init_segm_dics(self):
        '''
        Initialize the dictionaries for masks, contours, areas (of segmentations)
        '''
        nbcells = len(self.list_pos)
        self.dic_dilated_contours = { i:[] for i in range(nbcells)}    # dic for dilated contours
        self.dic_dil_cntrs_masks = { i:[] for i in range(nbcells) }    # dic for masks contours
        self.dic_mask_seg = { i:[] for i in range(nbcells) }           # dic for segmentation masks
        self.dic_segm_area = { i:0 for i in range(nbcells) }           # dic for cells area

    def dilate_and_save_mask_with_contours(self,i):
        '''
        Fill the dictionaries for masks and contours after dilation
        '''
        mask, contour = self.dilate_contour(i)
        self.dic_dilated_contours[i] = contour                       # save contour
        self.dic_dil_cntrs_masks[i] = mask                           # save the mask of the corresponding contour

    def pos_num(self,i):
        '''
        Position for the cell number in the picture
        '''
        shift = 5
        pos = np.array(self.list_pos[i])
        if pos[1] < 500:
            pos += np.array([-shift,shift])
        return tuple(pos)

    def insert_num_cell(self,i):
        '''
        number of the cell for tracking
        '''
        font = cv2.FONT_HERSHEY_SIMPLEX
        size = 0.3
        color = (255,)*3
        pos = self.pos_num(i)
        if self.args.num_cell:             # show the cell number
            cv2.putText(self.img, str(i), pos, font, size, color, 1, cv2.LINE_AA)

    # def choose_list_pos(self):
    #     '''
    #     '''
    #     if self.num > 0 :
    #         list_pos = self.list_prev_pos
    #     else:
    #         list_pos = self.list_pos
    #     return list_pos

    def identify_cell(self,i):
        '''
        Add color and number to the cell
        '''
        self.change_mask(i)              # change mask with bckgrd and neighbours
        try:
            self.fill_cell(i)
            self.insert_num_cell(i)      # show the Id num of the cell
        except:
            print('cannot fill cell ', i)

    def position_seed_bckgrd(self):
        '''
        '''
        seedpos = np.array(self.furthest_seed)
        shift = np.array([10,10])
        self.img = cv2.rectangle(self.img, tuple(seedpos-shift), tuple(seedpos+shift), (255,255,255), 2)
        #self.img = cv2.circle(self.img, self.furthest_seed, 50, (255,255,255), -1)

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
        if self.args.method == 2: # prediction
            self.img[mask > 254] = self.rand_col[i]    # color by thresholding with mask
        elif self.args.method == 1:   # Floodfill
            limupd = 100             # limit up down
            lod, upd = (limupd,)*4, (limupd,)*4   # fixed
            mask = cv2.bitwise_not(mask)
            cv2.floodFill( self.img, mask, seedPoint=self.list_pos[i], newVal=self.rand_col[i], loDiff=lod, upDiff=upd )

    def color_num_cell(self, i, mask):
        '''
        '''
        self.fill_pred(i,mask)       # fill the prediction mask with color
        self.insert_num_cell(i)      # show the Id num of the cell

    def cells_identification_simple(self, debug=0):
        '''
        Identify the cells
        '''
        list_pos = self.list_pos # self.choose_list_pos()
        self.curr_mask = {}
        for i, pos in enumerate(list_pos):
            if debug > 0: self.debug_pos_i(pos, i)
            if self.args.erode_after_pred:
                dil, iter_dil = self.dil_last_shape, self.iter_dil_last_shape
            else:
                dil, iter_dil = 1,1
            mask = self.make_mask_from_contour(self.curr_contours[i], dilate = dil, iter_dilate = iter_dil)  # mask from contours with dilation
            if self.args.track != 'all':
                if i in self.args.track:
                    self.color_num_cell(i,mask)  # color the cell and number it
            else:
                self.color_num_cell(i,mask)

    def cells_segmentation_with_floodfill(self, fill_bckgrd=False, show_seed_bckgd=True, debug=0):
        '''
        Segment the cells
        '''
        self.denoising() # optionnal denoising
        self.init_segm_dics()                                  # initialization of the dictionaries
        list_pos = self.list_pos # self.choose_list_pos()
        for i, pos in enumerate(list_pos):
            if debug > 0: self.debug_pos_i(pos, i)
            self.dilate_and_save_mask_with_contours(i)
            ##
        self.find_neighbours()
        self.make_mask_bckgd()
        for i, pos in enumerate(list_pos):
            #print("deal with cell ", i)
            if self.args.track != 'all':
                if i in self.args.track:
                    self.identify_cell(i)  # color the cell and number it
            else:
                self.identify_cell(i)
        if fill_bckgrd:
            self.fill_image_bckgrd()
        if show_seed_bckgd:                              # show the seed used for using the background as mask
            self.position_seed_bckgrd()
