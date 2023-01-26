import numpy as np
import cv2
from scipy.linalg import norm
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


class RAND_MOVE():
    '''
    Random walk..
    '''
    def __init__(self):
        '''
        Move at random
        '''

    def ask_for_xy(self):
        '''
        '''
        sleep(0.1)
        x_abs = self.pr.ask_pos('x')
        sleep(0.1)
        y_abs = self.pr.ask_pos('y')

        return x_abs, y_abs

    def make_relative_move_xy(self, dx, dy, debug=[]):
        '''
        Relative move in x and y
        '''
        if 0 in debug:
            print(f'dx,dy')
        # small correction for centering the cell
        self.pr.relative_move_to(dx, dy)
        # x, y positions
        x_abs, y_abs = self.ask_for_xy()
        z_abs = self.ol.ask_zpos()                # z position
        print(f'x_abs, y_abs, z_abs positions are  {x_abs, y_abs, z_abs} ')
        print('used in list_steps')
        # change the current position
        self.list_steps['posxyz'].val = [x_abs, y_abs, z_abs]

    def random_step(self, dist_max, debug=[]):
        '''
        dist_max : maximum distance in µm
        '''
        dx = np.random.randint(-dist_max, dist_max)
        dy = np.random.randint(-dist_max, dist_max)
        self.make_relative_move_xy(dx, dy)

    def make_relative_move_z(self, dz, debug=[]):
        '''
        Relative in z
        '''
        self.ol.set_zpos(dz, move_type='n')
        # x, y positions
        x_abs, y_abs = self.ask_for_xy()
        z_abs = self.ol.ask_zpos()                # z position
        print(f'x_abs, y_abs, z_abs positions are  {x_abs, y_abs, z_abs} ')
        print('used in list_steps')
        # change the current position
        self.list_steps['posxyz'].val = [x_abs, y_abs, z_abs]
        try:
            self.randz += [z_abs]
            with open(opj(self.dir_mda_temp, 'monitorings', 'AF', f'randz.pk'), "wb") as fw:
                pkl.dump(self.randz,fw)
        except:
            print('Cannot save randz')

    def random_z(self, dist_max, debug=[]):
        '''
        dist_max : maximum distance in µm
        '''
        dz = 100*np.random.randint(-dist_max, dist_max)
        print(f'random z dz = {dz} ')
        self.make_relative_move_z(dz)
