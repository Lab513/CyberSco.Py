'''
Camera Zyla
Installation :  in pyAndorSDK3, python3 –m pip install .
'''

import os
op = os.path
ospl = op.splitext
import numpy as np
from matplotlib import pyplot as plt
from skimage import io
from PIL import Image
##
from pyAndorSDK3 import AndorSDK3
#import pyfits as fits
import astropy.io.fits as fits

class ZYLA():
    '''
    '''
    def __init__(self):
        '''
        '''
        try:
            print ("\nConnecting to camera...")
            sdk3 = AndorSDK3()
            self.cam = sdk3.GetCamera(0)
            print (self.cam.SerialNumber)
        except:
            print('cannot open the cam')

    def adapt(self):
        '''
        Passing from 16 bits to 8 bits
        '''
        low = self.frame.min()       # lowest value in the image
        high = self.frame.max()      # Highest value in the image
        maxval = 256
        alpha = maxval/(high-low)
        print(f'self.frame.max() in 16 bits {self.frame.max()}')
        self.frame = (self.frame-low)*alpha   # change values of the image
        print(f'self.frame.max() in 8 bits {self.frame.max()}')

    def save_pic(self,addr,ext,bpp):
        '''
        Save the pic in tiff or png format
        '''
        if ext == '.tiff':
            if bpp == 16:
                io.imsave(addr, self.frame.astype(np.uint16))   # 16 bits
            elif bpp == 8:
                self.adapt()
                io.imsave(addr, self.frame.astype(np.uint8))    # 8 bits
        elif ext == '.png':
            self.adapt()
            img = Image.fromarray(self.frame.astype(np.uint8))
            img.save(addr)

    def take_pic(self, addr, bpp=16, exp_time=50, debug=[]):
        '''
        Retrieve a pic from the Zyla camera and save it in 16 bytes format
        '''
        name, ext = ospl(addr)
        if 1 in debug : print(f'extension is {ext}')
        print ("\nGetting image data...")
        self.frame = self.cam.acquire(timeout=20000).image.astype(np.float32)
        self.save_pic(addr,ext,bpp)

    def close(self):
        '''
        Close the camera
        '''
        self.cam.close()
