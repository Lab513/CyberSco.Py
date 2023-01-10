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

    def make_relative_move(self, dx, dy, debug=[]):
        '''
        Relative move for tracking
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
        # difference between nearest cell and the center
        dx = np.random.randint(0,dist_max)
        dy = np.random.randint(0,dist_max)
        # keep the position on the event at the center
        self.make_relative_move(dx, dy)
