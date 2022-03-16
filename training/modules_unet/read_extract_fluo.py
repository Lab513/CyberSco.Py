'''
Read the films and extract the pictures
'''
import os
opb = os.path.basename
opd = os.path.dirname
from pathlib import Path
import json
import shutil as sh
##
from PIL import Image
##
import numpy as np
##
from matplotlib import pyplot as plt
import cv2

class READ_EXTRACT_FLUO():
    '''
    Read video and extract images
    '''

    def extract_fluo(self, addr_fluo, kind_fluo):
        '''
        Extract the images from the video
        and save them in self.output_folder
        as self.size x self.size pictures with extension self.ext..
        '''
        self.kind_fluo = kind_fluo
        self.prepare_folders()
        self.addr_fluo = addr_fluo
        self.ext = os.path.splitext(addr_fluo)[1]
        print('#### extension is {0} !!! '.format(self.ext))
        if self.ext in ['.mp4','.avi']:
            self.read_extract_avi()
        elif self.ext == '.tif':
            self.read_extract_tif()

    def remove_folders(self):
        '''
        Remove the temporary folders:
            prediction/movie
            test/movie
            test/movie_fluo
        '''
        lfolder = [ Path('imgs_fluo') ]
        for fold in lfolder:
            try:
                sh.rmtree(fold)
            except:
                pass

    def test_exists_mkdir(self, path):
        '''
        '''
        if not os.path.exists(str(path)):
            os.mkdir(str(path))

    def prepare_folders(self):
        '''
        Make the output folders
        '''
        self.remove_folders()
        self.output_fluo = Path('imgs_fluo')
        self.test_exists_mkdir(self.output_fluo)

    def read_extract_avi(self):
        '''
        Read avi video and extract images
        '''
        vidcap = cv2.VideoCapture(self.addr_fluo)
        success, img = vidcap.read()
        count = 0
        while success:
            addr_img = str(self.output_fluo / f'fluo{self.kind_fluo}' / f"frame{count}{self.ext}")
            print(addr_img)
            cv2.imwrite( addr_img, img )     # save frame in self.output_folder
            success, img = vidcap.read()
            count += 1

    def resize_img(self, img, debug=0):
        '''
        Resize the images to the size : self.size
        '''
        res = cv2.resize(img, dsize=(self.size, self.size), interpolation=cv2.INTER_CUBIC) # dsize=(512, 512)
        if debug > 0:
            print("res.shape ", res.shape)
        ##
        dpi_val = 100
        fig = plt.figure(figsize=(self.size/dpi_val, self.size/dpi_val), dpi=dpi_val)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(res, aspect='equal', cmap='gray')
        return fig

    def read_extract_tif(self):
        '''
        Read tif videos and extract images
        '''
        print("The selected stack is a .tif")
        dataset = Image.open(self.addr_fluo)
        h,w = np.shape(dataset)
        for i in range(dataset.n_frames):
            addr_img = str(self.output_fluo / f'fluo{self.kind_fluo}' / f"frame{i}{self.ext}")
            print(addr_img)
            dataset.seek(i)
            img = np.array(dataset).astype(np.double)
            #print("img.shape ", img.shape)
            fig = self.resize_img(img)
            plt.savefig( addr_img, dpi=100 )       # save frame in self.output_folder
            plt.close(fig)
