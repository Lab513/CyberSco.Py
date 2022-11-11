import os, glob, re
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join
from time import sleep, time
from colorama import Fore, Back, Style
from pathlib import Path
import shutil as sh
import yaml
from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import cv2

class FIND_OPTIM_FOCUS():
    '''
    '''
    def __init__(self):
        '''
        '''
        self.prec_min = 0.05                                                          # precision for the max surface

    def search_optim_simple_sweep(self, ref, rep, AF_train,
                                  save_pic=True, corr_ind=0, debug=[]):
        '''
        Search the optimal AF pos making a simple sweep on fixed range..
        '''
        t0 = time()
        self.go_zpos(ref)
        l_surf, l_lap = self.make_surf_pred_list(ref)                               # make the list of surfaces in function of z
        if 0 in debug:
            print(f'l_surf, l_lap are  {l_surf, l_lap}')
        self.max_surf = max(l_surf)                                                 # maximal surface of segmentation
        t1 = time()
        ##
        ind_lap_optim = l_lap.index(max(l_lap))                                   # optimal index for Laplacian
        self.list_focusLap_index += [ind_lap_optim]
        self.debug_l_lap(l_lap)                                                     # plot curve for optimizing z with Laplacian
        if save_pic:
            self.take_pic_at_optim(ind_lap_optim, ref, rep, kind='Lap')
        ##
        ind_optim = self.find_optim(l_surf)                                         # find optim
        ind_optim += corr_ind                                                         # systematic correction
        if save_pic:
            self.take_pic_at_optim(ind_optim, ref, rep, kind='ML')
        if AF_train: self.make_AF_ML_direct_training(ref, rep, ind_optim)           # dataset for AF ML direct..
        self.debug_l_surf(l_surf, ind_optim)                                          # plot curve for optimizing z with ML
        pos_focus = ref + ind_optim*self.step_focus                                   # optimal z position for focus
        self.debug_lap_vs_surf(l_lap, l_surf)
        self.debug_pos_zoptim_ML(pos_focus)                                           # plot z optim in function of rep
        self.messages_refocus_segm(t0, t1, ind_optim, pos_focus)
        return pos_focus

    def af_optim_telapsed(self,t0,debug=[0]):
        '''
        Time elapsed for performing the AF with ML
        '''
        t1 = time()
        telapsed = round((t1-t0),1)
        self.list_AFML_duration += [telapsed]
        af_durations = opj('mda_temp', 'monitorings', 'AF', 'ML', 'AF_durations.png')
        plt.figure()
        plt.title('AFML durations')
        plt.ylim(0,20)
        plt.xlabel('iterations')
        plt.ylabel('time(s)')
        plt.plot(self.list_AFML_duration)
        plt.savefig(af_durations)
        if 0 in debug: print(f'self.list_AFML_duration is {self.list_AFML_duration} ')
        print(Fore.YELLOW +  f'time elapsed for AF is {telapsed} s ')
        print(Style.RESET_ALL)

    def searching_around_up_down(self, surf0, pos_focus, debug=[]):
        '''
        Search the optimum up and down, around the first z position
        needs a self.max_curve registered
        '''
        self.lsurf = []
        lpos_focus = []
        old_surf = surf0
        dist = 1
        prec = abs(surf0 - self.max_curve) / self.max_curve
        while (prec > self.prec_min and (surf0 >= old_surf)):
            if 2 in debug: print(f'Current distance is {dist}')
            old_surf = surf0
            pos_focus_low = pos_focus - dist*self.step_focus                      # low pos
            pos_focus_high = pos_focus + dist*self.step_focus                     # high pos
            surf_low = self.find_surf(pos_focus_low)
            surf_high = self.find_surf(pos_focus_high)
            surf0 = max(surf_low, surf_high)
            print(f'surf0 self.max_curve {surf0, self.max_curve}')
            print(f'In searching_around_up_down, prec is {prec}')
            self.lsurf += [surf0]
            if surf_low > surf_high:
                lpos_focus += [pos_focus_low]
            else:
                lpos_focus += [pos_focus_high]
            dist += 1
            prec = abs(surf0 - self.max_curve) / self.max_curve

        if surf0 < old_surf :
            try:
                pos_focus = lpos_focus[-2]                             # posz one step back
                surf_max = self.lsurf[-2]                              # max surf one step back
            except:
                print('lpos_focus[-2] does not exist')
                print(f'using old_surf {old_surf} for surf_max ')
                surf_max = old_surf
        else :
            pos_focus = lpos_focus[-1]                                 # last posz
            surf_max = self.lsurf[-1]                                  # last max surf

        return pos_focus, surf_max

    def plot_lsurf(self, rep):
        '''
        Plot the list of the surfaces
        '''
        plt.figure()
        plt.title('lsurf with time')
        plt.plot(self.lsurf)
        addr_lsurf = opj('mda_temp', 'monitorings', 'AF', 'ML', f'lsurf_{rep}.png')
        plt.savefig(addr_lsurf)

    def search_near_steep_slope(self, pos_focus, debug=[1,2,3]):
        '''
        '''
        pos_focus -= 50
        surf_inf = self.find_surf(pos_focus)
        prec = abs(surf_inf - self.max_curve) / self.max_curve
        while prec  < self.prec_min:                                             # searcing near the left steep slope
            if 3 in debug: print('getting nearer from the steep slope.. ')
            pos_focus -= 50
            surf_inf = self.find_surf(pos_focus)
            prec = abs(surf_inf - self.max_curve) / self.max_curve
            if 3 in debug:
                print(f'pos_focus is {pos_focus}')
                print(f'surf_inf is {surf_inf}')
        self.optim_posz = pos_focus                                              # save pos z at optimum

        return pos_focus

    def optim_with_max_around(self, ref, rep, AF_train, follow_max_curve=True, debug=[1,2,3]):
        '''
        begin with previous optimal posz and search up and down alternatively
        .. until reaching value close to the max.
        ref: pos z of reference
        rep: iteration
        AF_train :
        '''
        if rep == 0:                                                                          # complete scan
            pos_focus = self.search_optim_simple_sweep(ref, rep, AF_train)
            self.optim_posz = pos_focus
            if 1 in debug: print(f'At rep = 0, self.optim_posz is {self.optim_posz} ')
            self.max_curve = max(self.ref_l_surf)                                             # max
        else:
            t0 = time()
            print(f'using self.optim_posz {self.optim_posz} !!')
            surf0 = self.find_surf(self.optim_posz)
            pos_focus = self.optim_posz
            prec = abs(surf0 - self.max_curve) / self.max_curve
            print(f'at first try, surf0 self.max_curve {surf0, self.max_curve}')
            if prec > self.prec_min:
                print(f'### prec > self.prec_min, need to be more precise ')
            else:
                print(f'At optimum, surf0 self.max_curve are {surf0, self.max_curve}')
                self.af_optim_telapsed(t0)
                return pos_focus                                                     # focus found
            pos_focus, surf_max = self.searching_around_up_down(surf0, pos_focus)
            # pos_focus -= 100                                                          # removing 1 µm to avoid fuzzy pictures
            print(f'for rep {rep} the optimal pos_focus is {pos_focus}')
            self.af_optim_telapsed(t0)
            ##
            self.plot_lsurf(rep)

            if follow_max_curve:
                self.max_curve = surf_max
            ## searching near steep slope
            pos_focus = self.search_near_steep_slope(pos_focus)

        return pos_focus

    def print_lists_step(self, step, lposz, lsurf):
        '''
        print dichotomy values..
        '''
        print(f'step = {step}')
        print(f'lposz = {lposz}')
        print(f'lsurf = {lsurf}')

    def time_dicho(self, t0):
        '''
        Time for performing the dichotomy
        '''
        t1 = time()
        telapsed = round((t1-t0),1)
        print(Fore.YELLOW +  f'##### time elapsed for dichotomy is {telapsed}')
        print(Style.RESET_ALL)

    def optim_with_dichotomy(self, rep, AF_train, debug=[1,2,3]):
        '''
        begin with previous optimal posz and search up and down alternatively
        .. until reaching value close to the max.
        rep: iteration
        AF_train : save informations concerning AF for using it for ML or other purposes..
        Around 2.5s per image..
        '''
        t0 = time()
        step = 200                                                                  # beginning step is 2 µm
        lposz = [self.ref_posz - step, self.ref_posz, self.ref_posz + step]
        lsurf = []
        min_step = 100                                                              # last step 1µm
        print(f'## self.ref_posz is {self.ref_posz}')
        print(f'## lposz is {lposz}')
        print('Begin dichotomy focus !!!')
        for pz in lposz:
            lsurf += [self.find_surf(pz)]
        while 1:
            print(f'## Before improving, lsurf is {lsurf}')
            print('Positionning the max inside..')
            ind_maxsurf = lsurf.index(max(lsurf))
            if ind_maxsurf == 0:
                lsurf.insert(0, self.find_surf(lposz[0] - step))
                lposz.insert(0, lposz[0] - step )
                break
            elif ind_maxsurf == len(lsurf)-1:
                lsurf += [self.find_surf(lposz[-1] + step)]
                lposz += [lposz[-1] + step ]
                break
            else:
                break
        step /= 2                                                                # reduce the step size
        while 1:
            print('Searching the max..')
            ind_maxsurf = lsurf.index(max(lsurf))
            s0 = self.find_surf(lposz[ind_maxsurf] - step)
            s1 = self.find_surf(lposz[ind_maxsurf] + step)
            print(f'### max(lsurf) = {max(lsurf)}, s0 = {s0}, s1 = {s1}')

            if s0 > max(lsurf) and s0 > s1 and step >= min_step:                 # check position under max
                print('insert max value below')
                lposz.insert(ind_maxsurf - 1, lposz[ind_maxsurf] - step)
                lsurf.insert(ind_maxsurf - 1, s0)
                self.print_lists_step(step, lposz, lsurf)
                self.time_dicho(t0)

            elif s1 > max(lsurf) and s1 > s0 and step >= min_step:               # check position above max
                print('insert max value above')
                lposz.insert(ind_maxsurf + 1, lposz[ind_maxsurf] + step)
                lsurf.insert(ind_maxsurf + 1, s1)
                self.print_lists_step(step, lposz, lsurf)
                self.time_dicho(t0)

            else:                                                                # finished !
                pos_focus = lposz[ind_maxsurf]
                print('############# The end of dichotomy ########')
                print(f'optimum is {pos_focus} ')
                self.print_lists_step(step, lposz, lsurf)
                self.time_dicho(t0)
                return pos_focus
            step /= 2                                                            # reduce the step size
