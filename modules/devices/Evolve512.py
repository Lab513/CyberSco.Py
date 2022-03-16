'''
Class for controlling the camera Evolve 512
'''

from skimage import io
from PIL import Image
import numpy as np
import os
op = os.path
ospl = op.splitext
from colorama import Fore, Style

try:
    from pyvcam import pvc
    from pyvcam.camera import Camera
except:
    print('Did not find Evolve pyvcam')


class EVOLVE():
    '''
    '''
    def __init__(self):
        '''
        '''
        try:
            pvc.init_pvcam()                           # Initialize PVCAM
            # Use generator to find first camera.
            self.cam = next(Camera.detect_camera())
            self.cam.open()                            # Open the camera.
            print('#####')
            print(Fore.GREEN + 'opened correctly the Evolve512 camera  !!')
            print(Style.RESET_ALL)
            print('#####')
        except:
            print('###')
            print(Fore.RED + 'Cannot open the cam Evolve512 !!!')
            print(Style.RESET_ALL)
            print('###')

    def adapt(self, debug=[]):
        '''
        Passing from 16 bits to 8 bits
        '''
        low = self.frame.min()       # lowest value in the image
        high = self.frame.max()      # Highest value in the image
        maxval = 256
        alpha = maxval/(high-low)
        if 1 in debug:
            print(f'self.frame.max() in 16 bits {self.frame.max()}')
        # change the image pixels values.
        self.frame = (self.frame-low)*alpha
        if 2 in debug:
            print(f'self.frame.max() in 8 bits {self.frame.max()}')

    def save_pic(self, addr, ext, bpp):
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

    def take_pic(self, addr=None, bpp=16, exp_time=50, debug=[]):
        '''
        Retrieve a pic from Evolv 512 and save it in 16 bytes format
        '''
        self.cam.speed_table_index = 0
        self.frame = self.cam.get_frame(exp_time=exp_time)
        if addr:
            name, ext = ospl(addr)
            if 1 in debug:
                print(f'extension is {ext}')
            self.save_pic(addr, ext, bpp)

    def close(self):
        '''
        Close the camera
        '''
        self.cam.close()
