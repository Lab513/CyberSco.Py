import os, sys
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename
import shutil as sh
from collections import defaultdict
import time
from time import sleep
from datetime import datetime
import numpy as np
from matplotlib import pyplot as plt
from pathlib import Path
from colorama import Fore, Back, Style
##
from modules.util_server import *
from modules.util_misc import *

import cv2

class HOG1():
    '''
    '''
    def __init__(self):
        pass

    def make_hog1_whole_cell_and_nucleus_curves(self, debug=[1]):
        '''

        '''
        for k,v in self.list_cells_gfp_intens.items():
            plt.figure()
            addr_pic_gfp_cells = opj(self.dir_mda_temp, 'monitorings', 'experim', f'hog1_whole_cells.png')
            try:
                plt.ylim(0,max(v)*1.3)
            except:
                pass
            plt.plot(v)
            plt.savefig(addr_pic_gfp_cells)
            plt.close()
        if 1 in debug:
            print(f'####### The list is {self.list_cells_gfp_intens}')
            print(f'Created figures for cells !!!')
        for k,v in self.list_nucleus_gfp_intens.items():
            plt.figure()
            addr_pic_gfp_nucleus = opj(self.dir_mda_temp, 'monitorings', 'experim', f'hog1_whole_nuclei.png')
            try:
                plt.ylim(0,max(v)*1.3)
            except:
                pass
            plt.plot(v)
            plt.savefig(addr_pic_gfp_nucleus)
            plt.close()
        if 1 in debug:
            print(f'####### The list self.list_nucleus_gfp_intens is {self.list_nucleus_gfp_intens}')
            print(f'Created figures for nucleus !!! ')

    def make_hog1_each_cell_and_nucleus_curves(self, debug=[]):
        '''
        Plot and save the curves for the intensities of GFP in each cell and each nucleus..
        '''
        for k,v in self.list_cells_gfp_intens.items():
            plt.figure()
            addr_pic_gfp_cells = opj(self.dir_mda_temp, 'monitorings', 'experim', f'hog1_cell{k}.png')
            try:
                plt.ylim(0,max(v)*1.3)
            except:
                pass
            plt.plot(v)
            plt.savefig(addr_pic_gfp_cells)
            plt.close()
        if 1 in debug:
            print(f'####### The list is {self.list_cells_gfp_intens}')
            print(f'Created figures for cells !!!')
        for k,v in self.list_nucleus_gfp_intens.items():
            plt.figure()
            addr_pic_gfp_nucleus = opj(self.dir_mda_temp, 'monitorings', 'experim', f'hog1_nucleus{k}.png')
            try:
                plt.ylim(0,max(v)*1.3)
            except:
                pass
            plt.plot(v)
            plt.savefig(addr_pic_gfp_nucleus)
            plt.close()
        if 1 in debug:
            print(f'####### The list self.list_nucleus_gfp_intens is {self.list_nucleus_gfp_intens}')
            print(f'Created figures for nucleus !!! ')

    def hog1_make_lists_whole_cells(self, nb_cells_max = 40, debug=[1,2]):
        '''
        Lists of the intensities of GFP for each cell and each nucleus
        '''
        if 1 in debug: print(f"################# len(self.curr_cntrs) {len(self.curr_cntrs)}")
        intens_gfp_cell = 0
        for i,c in enumerate(self.curr_cntrs):
            try:
                mask = self.mask_from_cntr(c)
                cell_area = cv2.contourArea(c)
                if cell_area !=0:
                    intens_gfp_cell += self.img_gfp[mask == 255].sum()/cell_area
                else:
                    intens_gfp_cell = 0
            except:
                pass
            if 1 in debug: print(f'intens_gfp_cell {intens_gfp_cell}')
            if i> nb_cells_max: break
        self.list_cells_gfp_intens[0] +=  [intens_gfp_cell]                                 # GFP normalized intensity in the cell
        if 2 in debug: print(f"################# self.list_cells_gfp_intens {self.list_cells_gfp_intens}")
        ####
        intens_gfp_nucleus = 0
        for i,c in enumerate(self.img_rfp_cntrs):
            try:
                mask = self.mask_from_cntr(c)
                cell_area = cv2.contourArea(c)
                if cell_area !=0:
                    intens_gfp_nucleus += self.img_gfp[mask == 255].sum()/cell_area
                else:
                    intens_gfp_nucleus = 0
            except:
                pass
            if i> nb_cells_max: break
        self.list_nucleus_gfp_intens[0] += [intens_gfp_nucleus]                                 # GFP normalized intensity in the nucleus
        if 2 in debug: print(f"################# self.list_nucleus_gfp_intens {self.list_nucleus_gfp_intens}")

    def hog1_make_lists_each_cell(self, debug=[]):
        '''
        Lists of the intensities of GFP for each cell and each nucleus
        '''
        if 1 in debug: print(f"################# len(self.curr_cntrs) {len(self.curr_cntrs)}")
        for i,c in enumerate(self.curr_cntrs):
            try:
                mask = self.mask_from_cntr(c)
                cell_area = cv2.contourArea(c)
                if cell_area !=0:
                    intens_gfp_cell = self.img_gfp[mask == 255].sum()/cell_area
                else:
                    intens_gfp_cell = 0
            except:
                intens_gfp_cell = 0
            if 1 in debug: print(f'intens_gfp_cell {intens_gfp_cell}')
            self.list_cells_gfp_intens[i] += [intens_gfp_cell]                                  # GFP normalized intensity in the cell
        for c in self.img_rfp_cntrs:
            pos = self.pos_from_cntr(c)
            ind = self.find_nearest_index_BF_fluo(pos)
            try:
                mask = self.mask_from_cntr(c)
                cell_area = cv2.contourArea(c)
                if cell_area !=0:
                    intens_gfp_nucleus = self.img_gfp[mask == 255].sum()/cell_area
                else:
                    intens_gfp_nucleus = 0
            except:
                intens_gfp_nucleus = 0
            self.list_nucleus_gfp_intens[ind] += [intens_gfp_nucleus]                           # GFP normalized intensity in the nucleus

    def hog1_curves(self, rep, freq=2, all_cells=False, debug=[]):
        '''
        Curves of evolution of GFP intensity in each cell and each nucleus
        '''
        t0 = time.time()
        if rep == 0:
            self.list_nucleus_gfp_intens = defaultdict(list)
            self.list_cells_gfp_intens = defaultdict(list)
        addr_pic_gfp = opj(self.dir_mda_temp, f'frame{self.num}_gfp_t{rep}.tiff')
        self.img_gfp = cv2.imread(addr_pic_gfp)
        addr_pic_rfp = opj(self.dir_mda_temp, f'frame{self.num}_rfp_t{rep}.tiff')
        _, self.img_rfp_cntrs = self.find_contours_otsu(addr_pic_rfp)
        if 1 in debug:
            print(f'len(self.img_rfp_cntrs) is {self.img_rfp_cntrs} ')
        if all_cells:
            self.hog1_make_lists_whole_cells()
        else:
            self.hog1_make_lists_each_cell()
        if rep%freq==0:
            if all_cells:
                self.make_hog1_whole_cell_and_nucleus_curves()
            else:
                self.make_hog1_each_cell_and_nucleus_curves()
        t1 = time.time()
        time_elapsed = round((t1-t0),2)
        print(f'time elapsed for hog1 curves is : {time_elapsed} ')
