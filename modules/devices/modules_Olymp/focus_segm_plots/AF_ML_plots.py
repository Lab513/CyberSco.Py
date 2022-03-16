'''
Plots for AF_ML method
'''

import os
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join
from time import sleep, time
from colorama import Fore, Back, Style
from pathlib import Path
import shutil as sh
import pickle as pk
import yaml
from matplotlib import pyplot as plt
import numpy as np
from scipy.optimize import curve_fit
import cv2
try:
    from modules_mda.plot_bokeh import BOKEH_PLOT
except:
    from modules.modules_mda.plot_bokeh import BOKEH_PLOT

class FOCUS_SEGM_PLOT():
    '''
    Focus with segmentation
    The optimal focus is the z value corresponding to the maximal segmentation area.
    The steepest positive slope is used for finding the optimum.
    '''
    def __init__(self, nb_af_steps=8, delta_af=500):
        '''
        '''

    def save_pickle_curves(self, l_surf, kind):
        '''
        Save in pickle format the curves for AF optimization..
        '''
        addr_af = Path('mda_temp') / 'monitorings' / 'AF'
        addr_curves = addr_af / kind / f'af{kind}_optim_t{self.rep}.pk'
        pk.dump(l_surf, open(addr_curves , "wb"))

    def debug_l_surf(self, l_surf, ind_optim, save_curve=True):
        '''
        Plot l_surf
        '''
        plt.figure(figsize=(8,8))
        plt.title(f'Evol Surf t{self.rep}')
        plt.plot(l_surf)                                                        # plot evolution of pred surface
        x,y = ind_optim, l_surf[ind_optim]                                        # optimum position
        if save_curve: self.save_pickle_curves(l_surf, 'ML')
        plt.plot(x,y, 'go')                                                     # optimum with ML method on the cure of the surface
        plt.xlabel('iteration')
        if self.mean_surf:
            plt.ylabel('segmented surface')
        else:
            plt.ylabel('full surface')
        try:
            name_img = f'evol_surf_pred{self.num}_t{self.rep}.png'
            addr_img = Path('mda_temp') / 'monitorings' / 'AF' / 'ML' / name_img
            plt.savefig(addr_img, dpi=64)
        except:
            print('Cannot save l_surf')

    def debug_l_lap(self, l_lap, save_curve=True):
        '''
        Plot l_lap
        '''
        plt.figure(figsize=(8,8))
        plt.title(f'Evol Lap t{self.rep}')
        plt.plot(l_lap)                                                         # plot evolution of the Laplacian variance
        plt.xlabel('iteration')
        plt.ylabel('variance of the Laplacian')
        if save_curve: self.save_pickle_curves(l_lap, 'Lap')
        try:
            name_img = f'evol_lap_var{self.num}_t{self.rep}.png'
            addr_img = Path('mda_temp') / 'monitorings' / 'AF'/ 'Lap' / name_img
            plt.savefig(addr_img, dpi=64)
        except:
            print('Cannot save l_lap')

    def debug_lap_vs_surf(self, l_lap, l_surf, suffix = 'png', bokeh_fig=False):
        '''
        Compare Laplacian variance : l_lap with ML method : l_surf
        '''
        if bokeh_fig:
            plt = BOKEH_PLOT()
            suffix = 'html'
        try:
            plt.title('Lap vs Surf')
            indices = np.arange(len(l_lap))
            plt.plot(indices, np.array(l_lap)/max(l_lap), label='method Laplacian')             # plot evolution of normalized Laplacian
            plt.plot(indices, np.array(l_surf)/max(l_surf), label='method ML')
            plt.xlabel('iteration')
            plt.ylabel('a.u')
            ##
            name_img = f'evol_lap_surf{self.num}_t{self.rep}.{suffix}'
            addr_img = Path('mda_temp') / 'monitorings' / 'AF' / name_img
            plt.legend()
            plt.savefig(addr_img)
        except:
            print('Cannot make evol_lap_surf !!!')

    def follow_index_optim(self, ind_optim):
        '''
        Plot lists of the indices
        '''
        print(f'For pos {self.num} and rep {self.rep}, index_steepest is {ind_optim}')
        self.list_focusML_index += [ind_optim]

        ###  list of the indices for the ML method

        plt.figure()
        plt.xlabel('iterations')
        plt.ylabel('optimal index')
        plt.plot(self.list_focusML_index)
        name_img = f'list_focusML_index_pos{self.num}.png'
        addr_img = Path('mda_temp') / 'monitorings' / 'AF' / name_img           # save evolution of the optim index with ML method
        plt.savefig(addr_img)

        ### list of the indices for Laplacian method

        plt.figure()
        plt.xlabel('iterations')
        plt.ylabel('optimal index')
        plt.plot(self.list_focusLap_index)
        name_img = f'list_focusLap_index_pos{self.num}.png'
        addr_img = Path('mda_temp') / 'monitorings' / 'AF' / name_img           # save evolution of the optim index with Laplacian
        plt.savefig(addr_img)

        ###   Comparison of the list of the indices for both methods

        plt.figure()
        plt.xlabel('iterations')
        plt.ylabel('optimal index')
        plt.plot(self.list_focusML_index, label='ML')
        plt.plot(self.list_focusLap_index, label='Laplacian')
        plt.legend()
        name_img = f'list_both_methods_index_pos{self.num}.png'
        addr_img = Path('mda_temp') / 'monitorings' / 'AF' / name_img           # Comparing index for both methods
        plt.savefig(addr_img)

        ###   optim Lap - optim ML

        plt.figure()
        plt.xlabel('iterations')
        plt.ylabel('ml - lap optimal index')
        ml = np.array(self.list_focusML_index)
        lap = np.array(self.list_focusLap_index)
        plt.plot(ml-lap)
        name_img = f'ml_minus_lap_optim-index_pos{self.num}.png'
        addr_img = Path('mda_temp') / 'monitorings' / 'AF' / name_img           # Comparing index for both methods
        plt.savefig(addr_img)

    def func_exp(self, x, a, b, c):
        '''
        Function for fitting an exponential on growth curves
        '''
        return a * np.exp(-b * x) + c

    def fit_on_zpos(self,xarray,yarray):
        '''
        Fit on zpos
        '''
        params = curve_fit(self.func_exp, xarray, yarray, bounds=(0, [1e2, 1e0, 1e4]))     # Perform the exponential fit
        yfitted = self.func_exp(xarray,*params[0])

        return xarray, yfitted

    def plot_fit_zpos(self):
        '''
        Plot the fit on zpos values during iterations
        '''
        x = np.arange(len(self.list_focusML_zpos))
        y = np.array(self.list_focusML_zpos)
        xfit, yfit = self.fit_on_zpos(x,y)
        plt.plot(xfit, yfit)

    def debug_pos_zoptim_ML(self, pos_focus, suffix = 'png', bokeh_fig=True, debug=[]):
        '''
        Figure of the optimal z position with ML method
        '''
        # try:
        if 1 in debug: print(f'Before plotting Bokeh')
        if bokeh_fig:
            plt = BOKEH_PLOT()
            suffix = 'html'
        self.list_focusML_zpos += [pos_focus/100]
        plt.xlabel('iterations')
        plt.ylabel('position of the focus (µm)')
        indices = np.arange(len(self.list_focusML_zpos))
        plt.plot(indices, self.list_focusML_zpos)                             # plot zpos
        try:
            self.plot_fit_zpos()                                                # exponential fit
        except:
            print('Cannot plot the fit for pos z !!!')
        plt.title('zpos in function of rep')
        name_img = f'list_focusML_z_pos{self.num}.{suffix}'
        addr_img = Path('mda_temp') / 'monitorings' / 'AF' / name_img           # evolution of the focus
        plt.show()
        plt.savefig(addr_img)
        if 1 in debug: print(f'Plotting Bokeh done !!!')
        # except:
        #     print('Cannot plot zoptim_ML')
