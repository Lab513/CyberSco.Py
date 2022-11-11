'''
Class for controlling the camera Evolve 512
'''

try:
    from modules.devices.camera_util.cam_util import CAM_UTIL as CU
except:
    from devices.camera_util.cam_util import CAM_UTIL as CU
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


class EVOLVE(CU):
    '''
    '''
    def __init__(self, debug=[]):
        '''
        Open the camera
        '''
        CU.__init__(self)
        try:
            pvc.init_pvcam()                           # Initialize PVCAM
            # Use generator to find first camera.
            self.cam = next(Camera.detect_camera())
            self.cam.open()                            # Open the camera.
            if 0 in debug:
                print('#####')
                print(Fore.GREEN + 'opened correctly Evolve512 cam  !!')
                print(Style.RESET_ALL)
                print('#####')
        except:
            print('###')
            print(Fore.RED + 'Cannot open Evolve512 cam !!!')
            print(Style.RESET_ALL)
            print('###')

    def save_pic(self, addr, ext, bpp, contrast=False, debug=[0]):
        '''
        Save the pic in tiff or png format
        '''
        if 0 in debug:
            print(f'ext is {ext}')
            print(f'bpp is {bpp}')
            print(f'self.frame.min() = {self.frame.min()}')
            print(f'self.frame.max() = {self.frame.max()}')
        self.handle_contrast(contrast, bpp)
        kind_int = f'uint{bpp}'
        type_int = getattr(np, kind_int)
        frame = self.frame.astype(type_int)
        if ext == '.tiff':
            io.imsave(addr, frame)
        elif ext == '.png':
            img = Image.fromarray(frame)
            img.save(addr)

    def take_pic(self, addr=None, bpp=16, exp_time=50, allow_contrast=False, debug=[]):
        '''
        Retrieve a pic from Evolv 512 and save it in 16 bytes format
        addr:
        bpp: 16 for 16 bits, 8 for 8 bits..
        exp_time: exposure time
        allow_contrast: correction on min max and scale for better image..
        '''
        self.cam.speed_table_index = 0
        self.frame = self.cam.get_frame(exp_time=exp_time)
        if addr:
            name, ext = ospl(addr)
            if 1 in debug:
                print(f'extension is {ext}')
            self.save_pic(addr, ext, bpp, contrast=allow_contrast)

    def close(self):
        '''
        Close the camera
        '''
        self.cam.close()
