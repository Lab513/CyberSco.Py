import errno, os, sys, csv, json, glob, logging
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join
import shutil as sh
from time import sleep, time
import numpy as np
import cv2


class SWEEP():
    '''
    '''
    def __init__(self, pr, ol, dic_displ_obj, emit, server):
        '''
        '''
        self.pr = pr
        self.ol = ol
        self.dic_displ_obj = dic_displ_obj
        self.emit = emit
        self.server = server
        self.addr_pic = 'interface/static/curr_pic/frame0.png'
        # address for big_img
        self.addr_snap_sweep = 'interface/static/sweep_chip'

    def prepare_sweep(self, sweepings):
        '''
        Prepare variables before sweeping
        '''
        dic_sweep = json.loads(sweepings)
        self.swpx = int(dic_sweep['sweepx'])           # sweepx from interface
        self.swpy = int(dic_sweep['sweepy'])           # sweepy from interface
        print(f'sweepx is {self.swpx} ')
         # ratio from px to µm
        fact_micro = self.dic_displ_obj[self.ol.objective]
        # ratio for overlapping, if < 1 it overlaps
        ratio_img = 1
        self.step_img = int(ratio_img*512)
        self.step = int(fact_micro*self.step_img)                # step in µm
        self.x = self.pr.ask_pos('x')                            # x pos in µm
        self.y = self.pr.ask_pos('y')                            # y pos in µm
        self.x_sweep_ref = self.x
        self.y_sweep_ref = self.y
        # size x image in px
        self.dx = abs((int(self.swpx/self.step)+1)*self.step_img)
        # size y image in px
        self.dy = abs((int(self.swpy/self.step)+1)*self.step_img)
        print(f'self.dx = {self.dx}, self.dy = {self.dy} ')
        self.big_img = np.empty((self.dy, self.dx))
        # sweep size
        self.sweep_size = (int(self.swpx/self.step) +
                           1)*(int(self.swpy/self.step) + 1)
        self.list_bad_tiles = []                     # list of bad tiles
        self.lposx = range(int(self.x), int(self.x) - self.swpx, -self.step)
        self.lposy = range(int(self.y), int(self.y) + self.swpy, self.step)

    def save_snap_sweep(self, i, j, debug=[]):
        '''
        Save the current image from live view
        '''
        if not os.path.exists(self.addr_snap_sweep):
            os.mkdir(self.addr_snap_sweep)
        addr_targ = opj(self.addr_snap_sweep, f'snap_i{i}_j{j}.png')
        print(addr_targ)
        sh.copy(self.addr_pic, addr_targ)

    def take_pic_at_ij(self, i, j, posx, posy, send_curr_iter=True):
        '''
        Take the picture and emit the index of
        iteration on the whole iterations
        '''
        self.save_snap_sweep(i, j)
        print(f'i,j {i,j}')
        print(f'posx, posy {posx, posy}')
        if send_curr_iter:
            sweep_num = i*(int(self.swpy/self.step) + 1)+j+1
            print(f'sweep_num {sweep_num}')
            self.server.sleep(0.5)
            # ratio : nb pos done over total nb of pos
            self.emit('sweep_num', str(sweep_num) + '/' + str(self.sweep_size))
            t1 = time()
            # time elapsed at pos i,j
            telapsed = round((t1-self.t0)/60, 1)
            lasting_time = round((self.sweep_size/sweep_num-1)*telapsed, 1)
            # sending time elapsed for the sweep
            self.emit('sweep_tlast',
                      ' (lasting :' + str(lasting_time) + ' min)')
        sleep(0.5)
        img = cv2.imread(opj(self.addr_snap_sweep, f'snap_i{i}_j{j}.png'), 0)

        return img

    def sweep_img_corr_brigthness(self, img):
        '''
        Adapt the brightness for uniform brightness
        '''
        curr_bright = np.sum(img) / img.size
        # brightness correction
        img = self.brightness/curr_bright*img

        return img

    def insert_in_big_image(self, i, j, img, debug=[1]):
        '''
        '''
        # insert in big image
        self.big_img[j*self.step_img:(j+1)*self.step_img,
                     i*self.step_img:(i+1)*self.step_img] =\
            img[-self.step_img:, -self.step_img:]

        if 1 in debug:
            print('completed self.big_img !!!')

    def sweep_brigthness_correction(self, i, j, img, debug=[1]):
        '''
        '''
        # brightness of first image
        if i == 0 and j == 0:
            self.brightness = np.sum(img) / img.size
        try:
            img = self.sweep_img_corr_brigthness(img)   # brightness correction
        except:
            print('Cannot correct for brightness !!')
        return img

    def take_pic_and_fill_sweep(self, i, j, posx, posy, debug=[1]):
        '''
        Move, copy the picture and add it to numpy array self.big_img
        '''
        if 1 in debug:
            print(f'In take_pic_and_fill_sweep, posx = {posx} ')
            print(f'In take_pic_and_fill_sweep, posy = {posy} ')
        self.pr.absolute_move_to(posx, posy)
        sleep(1.0)                               # time in sec between each pic
        img = self.take_pic_at_ij(i, j, posx, posy)           # take pic
        if 2 in debug:
            print(f'### img.shape = {img.shape} ')
        img = self.sweep_brigthness_correction(i, j, img)
        try:
            self.insert_in_big_image(i, j, img)
        except:
            print('Cannot broadcast')
            self.list_bad_tiles += [[i, j]]     # save pos of bad tiles

    def correction_of_bad_tiles(self):
        '''
        Retrieving again the tiles badly taken on the first round
        '''
        print('Correcting bad tiles !!!!')
        print(f'after first round, '
              'self.list_bad_tiles is {self.list_bad_tiles} !!!')
        for i, j in self.list_bad_tiles:
            posx, posy = list(self.lposx)[i], list(self.lposy)[j]
            print(f'posx, posy are {posx, posy}')
            # retrieve missing images
            self.take_pic_and_fill_sweep(i, j, posx, posy)

    def sweep_chip(self, sweepings, corr=True, debug=[]):
        '''
        corr : correction on the tiles not retrieved correctly
        '''
        self.prepare_sweep(sweepings)

        #  Sweeping
        self.t0 = time()
        for i, posx in enumerate(self.lposx):          # make the sweep
            for j, posy in enumerate(self.lposy):
                # filling the big image
                self.take_pic_and_fill_sweep(i, j, posx, posy)
        if corr:
            self.correction_of_bad_tiles()
        # save the mosaic of the chip
        cv2.imwrite(opj(self.addr_snap_sweep, 'big_img.png'), self.big_img)
        # go back to the initial position
        self.pr.absolute_move_to(self.x, self.y)
        dic_dim_sweep = {'width': self.dx, 'height': self.dy,
                         'sweepx': self.swpx, 'sweepy': self.swpy}
        print(f'dic_dim_sweep is  {dic_dim_sweep} ')
        print(f'After second round, '
              f'self.list_bad_tiles is {self.list_bad_tiles} !!!')
        self.server.sleep(0.5)
        # send message the chip was  whole swept..
        self.emit('swept', json.dumps(dic_dim_sweep))

    def move_in_sweep(self, coords, debug=[]):
        '''
        When clicking in the picture, move where clicked..
        '''
        fact_micro = self.dic_displ_obj[self.ol.objective]
        dic_coords = json.loads(coords)
        print(f'dic_coords {dic_coords}')
        print(f'ref are self.x_sweep_ref : '
              f' {self.x_sweep_ref}, self.y_sweep_ref : {self.y_sweep_ref} ')
        corr_center = 192.3*fact_micro
        # µm  , correction for centering
        newx = self.x_sweep_ref - dic_coords['x'] + corr_center
        # µm  , correction for centering
        newy = self.y_sweep_ref + dic_coords['y'] - corr_center
        print(f'newx is {newx}, newy is {newy}')
        self.pr.absolute_move_to(newx, newy)
