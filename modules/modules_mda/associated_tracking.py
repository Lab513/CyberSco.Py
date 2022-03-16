from collections import defaultdict
import time
from pathlib import Path
from matplotlib import pyplot as plt
import numpy as np
from scipy.linalg import norm
from scipy.optimize import curve_fit
from modules.util_server import find_platform, chose_server
from modules.util_misc import *
from modules.track_segm.count_fluo import COUNT_FLUO as CF
import cv2
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename

platf = find_platform()
server = chose_server(platf)


class ASSOCIATED_TRACKS(CF):
    '''
    Associated Tracking
    '''
    def __init__(self):
        '''
        Associated Tracking
        '''
        self.cf = CF()
        self.list_buds_size_stopped = []
        # factor for nb of the fitting curve points
        self.fit_hist_fact = 4
        self.mature_size = 48                 # for 60x
        # minimal slope for triggering the observations
        self.trig_min_slope = 1.0
        # nb of points in the history for triggering
        self.trig_hist_length = 2

    def make_list_pos_fluo(self, debug=[]):
        '''
        Build the list of the fluo cells
        '''
        if 1 in debug:
            print(f'## len(self.cf.cntrs_fluo) is {len(self.cf.cntrs_fluo)} ')
        for c in self.cf.cntrs_fluo:
            x, y, w, h = cv2.boundingRect(c)
            pos = (int(x + w/2), int(y + h/2))  # find position
            # list of the positions associated with fluorescence
            self.list_pos_fluo.append(pos)

    def track_fluo(self, rep, kind_fluo='_RFP', debug=[]):
        '''
        Make the list of positions of the fluo cells
        '''
        self.list_pos_fluo = []
        name_pic, addr_pic = self.name_pic(rep, kind_fluo=kind_fluo)
        if 0 in debug:
            print(f'addr_pic is {addr_pic}')
        self.cf.detect_cells_fluo(addr_pic)
        self.make_list_pos_fluo()
        if 1 in debug:
            print(f'self.list_pos_fluo is {self.list_pos_fluo}')

    def find_nearest_index_BF_fluo(self, pos, debug=[]):
        '''
        Find indices in BF tracking of the fluo cells
        '''
        # array of the new positions for BF
        arr_pos = np.array(self.list_pos)
        # all distances from position pos
        self.list_distances = list(map(norm, (arr_pos - np.array(pos))))
        # find index of the closest new position..
        ind = np.argmin(self.list_distances)
        if 1 in debug:
            print('arr_pos[ind] {0}, pos {1}'.format(arr_pos[ind], pos))

        return ind

    def find_indices_fluo_cells(self, rep, kind_fluo='gfp', debug=[]):
        '''
        Make the list of the fluo cells indices from list of tracking BF
        '''
        self.track_fluo(rep, kind_fluo='_' + kind_fluo)
        self.list_fluo_cells = []
        for pos in self.list_pos_fluo:
            index_fluoBF = self.find_nearest_index_BF_fluo(pos)
            self.list_fluo_cells.append(index_fluoBF)
        if 1 in debug:
            print(f'indices of the fluo cells are {self.list_fluo_cells}')

    def find_fluo(self, rep, debug=[]):
        '''
        track fluo and find correspondences
        '''
        if 1 in debug:
            print(f'in find_fluo !!!')
        try:
            # find indices of the fluorecent cells
            self.find_indices_fluo_cells(rep, kind_fluo=self.event.name)
            # if event is detected, event stop to be searched
            if self.list_fluo_cells:
                self.event.happened = True
        except:
            print('Cannot find fluo')

    ############## Buds

    def detect_cells_bud(self, debug=[]):
        '''
        Take the event picture and find the contours of the buds
        Produce self.cntrs_buds
        '''
        if 0 in debug:
            print('in detect_cells_bud ')
            print(f'### self.num is {self.num}, self.rep is {self.rep}')
        name_img = f'pred_ev_frame{self.num}_t{self.rep}_cntrs.png'
        addr = Path('mda_temp') / 'monitorings' / 'cntrs' / name_img
        img = cv2.imread(str(addr))
        imgray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)             # img gray
        ret, thresh = cv2.threshold(imgray, 127, 255, 0)
        self.cntrs_buds, _ = cv2.findContours(thresh,
                                              cv2.RETR_TREE,
                                              cv2.CHAIN_APPROX_SIMPLE)[-2:]
        if 1 in debug:
            print(f'len(self.cntrs_buds) is {self.cntrs_buds} ')

    def make_list_pos_bud(self, debug=[]):
        '''
        Make the list of the buds positions for the buds found with model B105
        '''
        if 1 in debug:
            print(f'## len(self.cntrs_buds) is {len(self.cntrs_buds)}')
        # using contours from buds model
        for c in self.cntrs_buds:
            x, y, w, h = cv2.boundingRect(c)
            pos = (int(x + w/2), int(y + h/2))     # find position
            self.list_pos_bud.append(pos)

    def track_buds(self, rep, debug=[]):
        '''
        Make the list of positions of the budding cells
        '''
        if 0 in debug:
            print('in track_buds')
        self.list_pos_bud = []
        self.detect_cells_bud()       # find the contours
        self.make_list_pos_bud()      # list of the buds positions
        if 1 in debug:
            print(f'self.list_pos_bud is {self.list_pos_bud}')

    def find_nearest_index_BF_bud(self, pos, debug=[]):
        '''
        Find for the position pos the index of the cell the nearest in BF image
        '''
        # array of the new positions for BF
        arr_pos = np.array(self.list_pos)
        # all distances from position pos
        self.list_distances = list(map(norm, (arr_pos - np.array(pos))))
        # find index of the closest new position..
        ind = np.argmin(self.list_distances)
        if 1 in debug:
            print('arr_pos[ind] {0}, pos {1}'.format(arr_pos[ind], pos))

        return ind

    def find_indices_budding_cells(self, rep, debug=[]):
        '''
        Make the list of the fluo cells indices from list of tracking BF
        '''
        self.track_buds(rep)
        self.list_budding_cells = []
        for pos_bud in self.list_pos_bud:
            index_budBF = self.find_nearest_index_BF_bud(pos_bud)
            # list of the cells associated with budding
            # for the current position
            self.list_budding_cells.append(index_budBF)
        if 1 in debug:
            print(f'indices of the budding'
                  f' cells are {self.list_budding_cells}')

    def find_buds(self, rep, debug=[]):
        '''
        track buds and find correspondences
        '''
        if 1 in debug:
            print('in find_buds !!!')
        try:
            # find indices of the fluorescent cells
            self.find_indices_budding_cells(rep)
            # if event is detected, event stop to be searched
            if self.list_budding_cells:
                self.event.happened = True
        except:
            print('Cannot find buds')

    # ----------------------------------------------------------
    # ------------------------------------------- buds with size
    # ----------------------------------------------------------

    def plot_all_hist(self, maxl, maxval):
        '''
        Plot buds size by superimposing
        maxl : number of time points
        maxval : max value for all the hstories
        '''
        t0 = time.time()
        plt.figure()
        for k, v in self.dic_buds_hist.items():
            diffz = (maxl-len(v['time']))*[0]      # how many zeros for filling
            vfill = diffz + v['area']              # fill with 0
            plt.ylim(0, maxval*1.3)
            plt.xticks(np.linspace(0, self.list_time_axis[-1], num=10))
            try:
                plt.plot(self.list_time_axis, vfill, label=str(k))
            except:
                pass
        try:
            name_pic = f'buds_history_pos{self.num}.png'
            addr_pic = opj(self.dir_mda_temp, 'monitorings',
                           'tracking', name_pic)
            plt.legend()
            plt.savefig(addr_pic)
        except:
            pass
        plt.close()
        t1 = time.time()
        telapsed = round((t1-t0), 2)
        print(f'time for plotting all the buds history is {telapsed} sec')

    def func_bud_fit(self, x, a, b):
        '''
        Function for fitting the buds growth
        '''
        return a * x + b

    def fit_bud_history(self, x, y, limfit=1e5, debug=[0]):
        '''
        Fit on bud's history
        x : np.array
        y : np.array
        limfit : high/low limit value for fit search
        '''
        if 0 in debug:
            print(f'x.size {x.size}, y.size {y.size}')
        # Search range large enough for avoiding slope error for large time values..
        # Perform the fit
        self.params_bud_fit = curve_fit(self.func_bud_fit,
                                        x, y, bounds=(-limfit,
                                                      [limfit, limfit]))
        if 1 in debug:
            print(f'self.params_bud_fit is {self.params_bud_fit[0]} ')
        slope = round(self.params_bud_fit[0][0], 1)      # fit's slope
        xx = np.linspace(x.min(), x.max(), self.fit_hist_fact*x.size)
        yfit = self.func_bud_fit(xx, *self.params_bud_fit[0])

        return xx, yfit, slope

    def plot_fit_bud_hist(self, k, debug=[]):
        '''
        Plot the fit on the history of the bud
        '''
        x, vvfit, slope = self.dic_fit_buds_hist[k]    # fit from dictionary
        if 1 in debug:
            print(f'x, vvfit for plot are {x, vvfit}')
        plt.xlabel('time (min)')
        plt.ylabel('area')
        nb_pts = len(self.dic_buds_hist[k]['time'])
        deltat = round(max(x)-min(x), 1)
        max_val = round(vvfit[-1], 1)
        plt.title(f'bud {k} ({nb_pts}pts,'
                  f'Δt= {deltat} min, slope={slope} px/min, max={max_val}) ')
        plt.plot(x, vvfit, 'r--', label='fit_' + str(k))

    def plot_single_cell_hist(self, k, v, maxval):
        '''
        Plot the area history for one bud
        '''
        plt.figure()
        plt.ylim(0, maxval*1.3)
        plt.xticks(np.linspace(0, v['time'][-1], num=5))  # regular ticks
        if len(v) > 1:
            # evolution area curve
            plt.plot(v['time'], v['area'], label=str(k))
            try:
                self.plot_fit_bud_hist(k)    # fitting curve on bud's history..
            except:
                print(f'Cannot plot the fit for history of bud {k}')
        name_pic = f'buds{k}_history_pos{self.num}.png'
        addr_pic = opj(self.dir_mda_temp, 'monitorings', 'tracking', name_pic)
        plt.legend()
        plt.savefig(addr_pic)
        plt.close()

    def plot_all_hist_separately(self, maxval, around_lim=False, debug=[]):
        '''
        Plot buds size separately
        maxval : maximum value on all plots
        around_lim : if True, plot only the curves which
         are first point is under the limit and the last above the limit
        '''
        t0 = time.time()
        for k, v in self.dic_buds_hist.items():
            if around_lim:
                # size conditions
                cnd0 = v['area'][0] < self.mature_size
                cnd1 = v['area'][-1] > self.mature_size
                '''
                plot if last point is above mature_size value
                 and first point under mature_size
                '''
                if cnd0 and cnd1:
                    # plot single cell's history
                    self.plot_single_cell_hist(k, v, maxval)
            else:
                # plot single cell's history
                self.plot_single_cell_hist(k, v, maxval)
        t1 = time.time()
        telapsed = round((t1-t0), 2)
        print(f'time for plotting all the'
              f' buds history separately is {telapsed} sec')

    def hist_list_maxl_maxval(self):
        '''
        History list max length and max value
        '''
        maxl = 0                                   # maximal length in history
        maxval = 0                                 # maximal value in history
        for _, v in self.dic_buds_hist.items():
            if len(v['time']) > maxl:
                maxl = len(v['time'])              # max length of the list
            if max(v['area']) > maxval:
                maxval = max(v['area'])            # max value of area
        return maxl, maxval

    def plot_buds_hist(self, each_cell_hist=True,
                       all_cells_hist=False, debug=[1]):
        '''
        Plot the history of the buds
        '''
        if 1 in debug: print('### Plot buds history')
        maxl, maxval = self.hist_list_maxl_maxval()   # max length, max value
        if all_cells_hist:
            # plot all superimposed histories
            self.plot_all_hist(maxl, maxval)
        if each_cell_hist:
            self.plot_all_hist_separately(maxval)      # plot each bud history

    def draw_buds_in_BF(self, rep, debug=[1]):
        '''
        Draw the buds segmentation in the BF image, with cells index and time
        '''
        if 1 in debug:
            print(f'### draw the selected buds in BF image at iteration {rep}')
        img_bud = self.img_cam.copy()
        for i in self.list_buds:
            # draw the buds
            img_bud = cv2.drawContours(img_bud,
                                       [self.curr_cntrs[i]],
                                       -1, (255, 255, 255), -1)
            # insert ID num of the bud
            self.insert_num_cell(i, shift=10, img=img_bud, color=(0, 255, 0))
        # insert time informations
        self.insert_time_marks(img_bud)
        name_pic = f'buds_frame{self.num}_t{rep}.png'
        # addr bud_frame
        addr_pic = opj(self.dir_mda_temp, 'monitorings', 'tracking', name_pic)
        # save buds with size
        cv2.imwrite(addr_pic, img_bud)

    def curr_cnt_dist_from_center(self, cnt):
        '''
        Current distance form the center
        '''
        curr_pos = np.array(self.pos_from_cntr(cnt))
        dist_from_center = norm(np.array([256, 256]) - curr_pos)
        return dist_from_center

    def cnd_dist_center(self, cnt, dist_center, dist=30):
        '''
        Return boolean if asked the condition on the distance to the center
        '''
        dcenter = self.curr_cnt_dist_from_center(cnt)
        if dist_center:
            # distance to center is less than dist
            cnd_dist = dcenter < dist
        else:
            cnd_dist = True
        return cnd_dist

    def check_bud_size_conditions(self, i, cnd_area, cnd_dist,
                    cnd_stopped, cnd_convex, cnd_big_neighb, freq=1):
        '''
        Check conditons on bud
        '''
        if i % freq == 0:
            # printing the conditions
            print(f'for cntr {i} ')
            print(f'cnd_area is {cnd_area} ')
            print(f'cnd_dist is {cnd_dist} ')
            print(f'cnd_stopped is {cnd_stopped} ')
            print(f'cnd_convex is {cnd_convex}')
            print(f'cnd_big_neighb is {cnd_big_neighb}')
            all_conds = cnd_area and cnd_dist\
                and (not cnd_stopped) and cnd_convex
            print(f'*** all conditions verified {all_conds} ***')

    def test_bud_convexity(self, cnt, diff_max=20, debug=[]):
        '''
        Test if the contour is close to a circle
        cnt: contour
        diff_max : maximal difference beween area of
              the contour and area of the circle approximation
        '''
        try:
            (_, _), radius = cv2.minEnclosingCircle(cnt)
            circ_area = round(np.pi*radius**2, 1)
            cnt_area = cv2.contourArea(cnt)
            if 1 in debug:
                print(f'circ_area is {circ_area}, cnt_area is {cnt_area}')
            cnd_convex = abs(circ_area - cnt_area) < diff_max
        except:
            print('Cannot make ellipse approximation !!!')
            cnd_convex = False

        return cnd_convex

    def find_if_big_neighb(self, c, times_area_max=1, debug=[]):
        '''
        Find if the contour c has a big neighbour. Return a boolean
        '''
        if 0 in debug:
            print('In find_if_big_neighb !')
        rad = np.sqrt(self.area_max/np.pi)         # radius
        if 0 in debug:
            print(f'rad = {rad} ')
        curr_pos = np.array(self.pos_from_cntr(c))
        big_neighb = False
        # inferior limit of size for the neighbour
        lim_inf = times_area_max*self.area_max
        for i, posi in enumerate(self.list_pos):
            dist = norm(np.array(posi) - curr_pos)
            # condition on the distance
            cnd0 = dist < 4*rad
            if 0 in debug and cnd0:
                print(f'for neighbour {i}, ')
                if 1 in debug:
                    print(f'cnd0, dist < 3*rad is {cnd0} ')
            carea = cv2.contourArea(self.curr_cntrs[i])
            cnd1 = carea > lim_inf        # condition on surface
            if 2 in debug and cnd0:
                print(f'cnd1, area {carea} > lim_inf {lim_inf} is {cnd1} ')
            if cnd0 and cnd1:
                big_neighb = True         #  found a big neighbour
                break

        return big_neighb

    def fill_dic_bud_hist(self, i, rep, curr_time,
                          area, cnt, hist_max_time, debug=[]):
        '''
        Fill the dictionaries used for buds history
        '''
        if 0 in debug:
            print('In fill_dic_bud_hist...')
        # list of the cells followed as "buds"
        self.list_buds += [i]
        # history current time of the bud
        self.dic_buds_hist[i]['time'].append(curr_time)
        # history area of the bud
        self.dic_buds_hist[i]['area'].append(area)
        # history list of contours for each rep
        self.list_buds_hist_rep[rep].append([i, cnt])
        time_list = self.dic_buds_hist[i]['time']
        # if > hist_max_time (min)
        if (max(time_list) - min(time_list)) > hist_max_time:
            # add i to the list of stopped histories
            self.list_buds_size_stopped += [i]
        if 1 in debug:
            print(f'self.dic_buds_hist[{i}] '
                  f'is {dict(self.dic_buds_hist[i])}')

    def reinit_buds_hist(self, debug=[]):
        '''
        Reinitialize dictionaries related to buds history
        '''
        if 0 in debug:
            print('Reinitializing dictionaries related to buds history')
            print(f'In reinit_buds_hist at rep {self.rep} !!')
        # reinit the dictionary of the fits
        self.dic_fit_buds_hist = {}
        # reinit dictionary of buds history
        self.dic_buds_hist = defaultdict(lambda: defaultdict(lambda: []))
        self.list_buds_size_stopped = []
        if 2 in debug:
            print(f'self.dic_fit_buds_hist is {dict(self.dic_fit_buds_hist)}')
            print(f'self.dic_buds_hist is {dict(self.dic_buds_hist)}')

    def make_buds_history(self, dist_center,
                          rep, hist_max_time=40, debug=[]):
        '''
        Make the history of area for the segmented objects..
        dist_center : Boolean for taking into account
                        the distance to the center..
        rep : iteration
        hist_max_time : history maximum duration
        '''
        curr_time = float(self.time_elapsed())             # current time
        if 1 in debug:
            print('In make_buds_history..')
        for i, cnt in enumerate(self.curr_cntrs):
            area = cv2.contourArea(cnt)
            if 2 in debug:                    # bud's surface
                print('---------------------')
                print(f'bud {i} area is {area}')
            # bud's area condition
            cnd_area = (self.area_min < area < self.area_max)
            # distance from centrer condition
            cnd_dist = self.cnd_dist_center(cnt,dist_center)
            cnd_stopped = i in self.list_buds_size_stopped
            # convexity condition with circle
            cnd_convex = self.test_bud_convexity(cnt, diff_max=20)
            if cnd_area:
                # find if there is a big neighbour
                cnd_big_neighb = self.find_if_big_neighb(cnt)
            else:
                cnd_big_neighb = False
            if 2 in debug:
                self.check_bud_size_conditions(i, cnd_area,
                     cnd_dist, cnd_stopped, cnd_convex, cnd_big_neighb)
            # filter with size and distance to center
            if cnd_area and cnd_dist and (not cnd_stopped)\
                    and cnd_convex and cnd_big_neighb:
                self.fill_dic_bud_hist(i, rep, curr_time,
                                       area, cnt, hist_max_time)
        print(f'area min is {self.area_min}, area max is {self.area_max}')
        print('############################################')
        print(f'****** at iteration {rep},  list of potential'
              f' buds is {self.list_buds} ******* ')
        print('############################################')
        if 3 in debug:
            print(f'#### self.dic_buds_hist {self.dic_buds_hist} ')

    def test_buds_history(self, k, v, debug=[]):
        '''
        Make a test on the object's history to know if it is a viable object
         i.e a bud and a bud with a good slope
        '''
        step_time = np.diff(self.list_time_axis)[0]
        deriv_hist = np.diff(v[2:])/step_time         # derivative
        if 1 in debug:
            print(f'for bud {k}, derivative is {deriv_hist} ')
        fit_hist_var = deriv_hist.var()
        if 2 in debug:
            print(f'the variance of the derivative'
                  f' of the fit for bud  {k}, is {fit_hist_var} ')
        if fit_hist_var < 1:
            print('We have a good candidate !!')
            return True                # good candidate
        else:
            return False               # bad candidate

    def trig_time_with_fit(self, k, size_pred, size_trig):
        '''
        Make the dictionary with associated time for triggering..
        Can be used after for choosing on which cell to trigger..
        '''
        # time (absolute) at which the obs has to be triggered (in minute)
        trig_time = np.argmin(norm(size_pred-size_trig))
        self.bud_time_trig[k] = trig_time
        print(f'for bud {k} trig_time is {trig_time}')

    def make_fit_on_buds_history(self, debug=[]):
        '''
        Fit the buds history
        '''
        if 0 in debug:
            print('In make_fit_on_buds_history')
        # dictionary containing the fits on the buds history
        self.dic_fit_buds_hist = {}
        # dictionary for bud history
        self.bud_time_trig = {}
        # size at which the tracking is triggered
        size_trig = self.mature_size/0.260*self.fact_micro
        # time over which we make prediction of size evolution
        delta_future = 50
        for k, v in self.dic_buds_hist.items():
            time_in_future = v['time'][-1] + delta_future
            if 1 in debug:
                print(f"#### len(v['time']) is {len(v['time'])}")
            # do not take the first point
            x, vfit, slope = self.fit_bud_history(np.array(v['time']),
                                                  np.array(v['area']))
            if 2 in debug:
                print(f'x, vfit are {x, vfit}')
            # dictionary for the fitting points
            self.dic_fit_buds_hist[k] = [x, vfit, slope]
            time_line = np.linspace(0, time_in_future, 100)
            size_pred = self.func_bud_fit(time_line, *self.params_bud_fit[0])
            if len(v) > 2:
                # test if the object is a good candidate
                test_fit = self.test_buds_history(k, v)
                if test_fit:
                    # forseen absolute time for trigger
                    self.trig_time_with_fit(k, size_pred, size_trig)

    def find_mature_buds(self, debug=[]):
        '''
        Find cells which are big enough and add them to self.list_budding_cells
        Their history needs to be long enough, the last point in history
        must be above the mature_size
        and the growth rate needs to be above the slope value..
        '''
        self.list_budding_cells = []
        for k, v in self.dic_buds_hist.items():
            x, vfit, slope = self.dic_fit_buds_hist[k]
            last_point = round(vfit[-1], 1)
            len_hist = int(len(x) / self.fit_hist_fact)
            if 1 in debug:
                print(f'***cell num {k}, len_hist {len_hist},'
                      f' vfit[-1] = {last_point}, slope = {slope} ')
            if (len_hist > self.trig_hist_length-1) \
                    and (vfit[-1] > self.mature_size) \
                    and (slope > self.trig_min_slope):
                # add cell to list_budding_cells if mature enough
                self.list_budding_cells += [k]
        if 2 in debug:
            # list of the cells at the limit of anaphase
            print(f'** pos {self.num} and iteration'
                  f' {self.rep} self.list_budding_cells'
                  f' is {self.list_budding_cells}')

    def find_buds_with_size(self, rep, plot_buds_hist=True,
                            dist_center=False, debug=[1]):
        '''
        Find buds with size in BF segmentation
        If dist_center set True, take into account the distance to the center
         for keeping just the cells not too far from the center ..
        Fill self.list_budding_cells
        '''
        # area min accepted for the buds
        self.area_min = self.fact_micro*100
        # area max accepted for the buds
        self.area_max = self.fact_micro*280
        if 1 in debug:
            print(f'In find_buds_with_size at iteration {rep}...')
        self.list_buds = []
        self.make_buds_history(dist_center, rep)
        self.make_fit_on_buds_history()     # make the fits
        if plot_buds_hist:
            self.plot_buds_hist()      # plot the history of the buds
        self.draw_buds_in_BF(rep)      # superimpose buds found with BF image
        # among the the candidate in the given intervall,
        # find the most mature..
        self.find_mature_buds()
