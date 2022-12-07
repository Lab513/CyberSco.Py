'''
Camera Zyla
Installation :  in pyAndorSDK3, python3 –m pip install .
'''

from modules.devices.camera_util.cam_util import CAM_UTIL as CU
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

class ZYLA(CU):
    '''
    '''
    def __init__(self):
        '''
        '''
        CU.__init__(self)
        try:
            print ("\nConnecting to camera...")
            sdk3 = AndorSDK3()
            self.cam = sdk3.GetCamera(0)
            print (self.cam.SerialNumber)
        except:
            print('cannot open the cam')

    def save_pic(self, addr, ext, bpp):
        '''
        Save the pic in tiff or png format
        '''
        self.handle_contrast(bpp)
        kind_int = f'uint{bpp}'
        type_int = getattr(np, kind_int)
        frame = self.frame.astype(type_int)
        if ext == '.tiff':
            io.imsave(addr, frame)
        elif ext == '.png':
            img = Image.fromarray(frame)
            img.save(addr)

    def take_pic(self, addr, bpp=16, exp_time=50, debug=[]):
        '''
        Retrieve a pic from the Zyla camera and save it in 16 bytes format
        '''
        name, ext = ospl(addr)
        if 1 in debug : print(f'extension is {ext}')
        print ("\nGetting image data...")
        self.frame = self.cam.acquire(timeout=20000).image.astype(np.float32)
        self.save_pic(addr, ext, bpp)

    def close(self):
        '''
        Close the camera
        '''
        self.cam.close()
