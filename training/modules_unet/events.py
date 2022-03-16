import os
from pathlib import Path
import glob
from matplotlib import pyplot as plt
import numpy as np
from colorama import Fore, Back, Style

class EVENTS():
    '''
    Events
    '''

    def __init__(self):
        '''
        '''
        pass

    def read_tiff(self,addr_img):
        '''

        '''

        img = Image.open(addr_img).convert('L')
        img = np.array(img).astype(np.double)

        return img

    def make_slices(self, w=30):
        '''
        Slices for capturing mitosis event
        '''

        py, px = self.pos_obs_cells
        print(f"#### posx, posy : {px}, {py}")
        sx, sy = slice(px-w, px+w), slice(py-w, py+w)

        return sx, sy

    def save_img_region_rfp(self, mask):
        '''
        Save region with mitosis target event
        '''
        addr_img = str( Path('test') / 'events' / ('img'+ str(self.num) + '.tiff' ) )
        self.plt_img(mask)
        plt.savefig( addr_img )       # save frame in self.output_folder
        for f in glob.glob('test/events/*.png'):
            os.remove(f)

    def rfp_image_for_buds(self):
        '''
        Show only the region where we want to see the mitosis
        '''

        print(f" ## save fluo region image  for frame {self.num} ")
        print(f" ## self.beg_obs_bud is {self.beg_obs_bud} ")
        print(f" **** self.num is {self.num} ")

        addr_fluo = str(Path('test') / 'movie_fluo' / ( 'frame' + str(self.num) + '.' + self.ext) )
        self.curr_img_fluo = self.read_tiff(addr_fluo)
        mask = np.zeros((512,512))
        sx, sy = self.make_slices()
        mask[ sx, sy ] = self.curr_img_fluo[ sx, sy ]
        self.save_img_region_rfp(mask)

    def init_capt_mitosis(self,pos,beg,delay):
        '''
        '''
        print( f"### after 2 loops, self.num {self.num}" )
        self.pos_obs_cells = pos
        self.beg_obs_bud = self.num
        self.lim_inf_ev = self.beg_obs_bud + beg
        self.lim_sup_ev = self.lim_inf_ev + delay
        print( f'current self.beg_obs_bud is {self.beg_obs_bud}' )
        print( f"### liminf : {self.lim_inf_ev} , limsup : {self.lim_sup_ev}" )

    def capt_mitosis(self):
        '''
        '''

        print( "### inside beg_obs_bud" )
        print( f"### self.num {self.num}" )
        print( f"### liminf : {self.lim_inf_ev} , limsup : {self.lim_sup_ev}" )
        if self.lim_inf_ev < self.num  < self.lim_sup_ev :
            print( "### in the middle.. " )
            self.rfp_image_for_buds()          # save region rfp
        if self.num > self.lim_sup_ev:
            self.beg_obs_bud = None
            print( f"### new self.beg_obs_bud is  {self.beg_obs_bud}" )

    def extract_region_rfp(self, cell_nb=0):
        '''
        Trying to capture mitosis with buds detection..
        '''

        print( f'events list of indices is : {self.list_indices_events}' )
        print( f"####### self.num {self.num}" )
        delay = 6                      # delay for rfp images
        beg = 15                       # begin 10 images after buds detection
        for ind, pos in self.list_indices_events:
            if ind == cell_nb and not self.beg_obs_bud : # 19
                self.init_capt_mitosis(pos,beg,delay)
        if self.beg_obs_bud :
            self.capt_mitosis()

    def find_indices_events(self):
        '''
        Indices of cells associated to buds in buds detection etc..
        '''

        self.list_indices_events = []
        try:
            for i, pos in enumerate(self.list_pos_events):
                ind = self.find_nearest_index(i, self.list_pos_events)
                self.list_indices_events.append([ind, pos])
                self.circle_at_pos(pos, radius=20)                                      # circle at event position
            print(f"self.list_indices_events is {self.list_indices_events} !!!")
            self.extract_region_rfp(cell_nb=0)
        except:
            print('No events')
