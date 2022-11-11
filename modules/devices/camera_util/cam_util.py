from pathlib import Path
import oyaml as yaml
import json


class CAM_UTIL():
    '''
    Utilities functions for camera
    '''
    def __init__(self):
        self.retrieve_autocontrast()

    def retrieve_autocontrast(self, debug=[0]):
        '''
        '''
        with open('interface/settings/cam_params.yaml') as f_r:
            dic_cam_params = yaml.load(f_r, Loader=yaml.FullLoader)
            self.autocontrast = dic_cam_params['autocontrast']
            if 0 in debug:
                print(f'########### For BF autocontrast is {self.autocontrast}')

    def adapt(self, bpp, debug=[1]):
        '''
        Adapt min max
        '''
        low = max(self.frame.min(),1)       # lowest value in the image
        high = self.frame.max()      # Highest value in the image
        maxval = 2**bpp
        alpha = maxval/(high-low)
        if self.autocontrast:
            # change values range of the image
            self.frame = (self.frame-low)*alpha
        if 1 in debug:
            print('in adapt..')
            print(f'bpp is {bpp}')
            print(f'self.frame.min() = {self.frame.min()}')
            print(f'self.frame.max() = {self.frame.max()}')

    def handle_contrast(self, contrast, bpp, debug=[0]):
        '''
        Handle the contrast or reduce to 8 bits if asked..
        '''
        if contrast:
            if 0 in debug:
                print('apply the autocontrast..')
            self.autocontrast = True
            self.adapt(bpp)
        else:
            # if no contrast and 8 bits resolution
            if bpp == 8:
                self.frame = self.frame/256
