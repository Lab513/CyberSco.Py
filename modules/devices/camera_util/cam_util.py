from pathlib import Path
import oyaml as yaml
import json


class CAM_UTIL():
    '''
    Utilities functions for camera
    '''
    def __init__(self):
        self.retrieve_cam_params()

    def retrieve_cam_params(self, debug=[]):
        '''
        '''
        with open('interface/settings/cam_params.yaml') as f_r:
            dic_cam_params = yaml.load(f_r, Loader=yaml.FullLoader)
        self.autocontrast = dic_cam_params['autocontrast']
        self.bpp = dic_cam_params['bpp']
        if 0 in debug:
            print(f'########### For BF autocontrast is {self.autocontrast}')
            print(f'########### bpp is {self.bpp}')

    def adapt(self, bpp, debug=[]):
        '''
        Adapt min max, take into account the bpp value.
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

    def handle_contrast(self, bpp, debug=[0]):
        '''
        Handle the contrast or reduce to 8 bits if asked..
        '''
        if self.autocontrast:
            if 0 in debug:
                print('apply the autocontrast..')
            self.adapt(bpp)
        else:
            if 0 in debug:
                print('no autocontrast applied..')
            # if no autocontrast and 8 bits resolution
            if bpp == 8:
                self.frame = self.frame/255
