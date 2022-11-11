from time import time
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename
import shutil as sh
import oyaml as yaml
from tensorflow.keras import models

class LOAD_MODELS():
    '''
    '''

    def __init__(self):
        '''
        '''
        pass

    def load_main_model(self):
        '''
        Load the main segmentation model
        '''
        with open('modules/settings/curr_model.yaml') as f_r:
            curr_mod = yaml.load(f_r, Loader=yaml.FullLoader)
            self.curr_mod = self.load_model(curr_mod)        # main model

    def load_event_model(self):
        '''
        Load the model for event detection
        '''
        with open('modules/settings/event_model.yaml') as f_r:
            ev_mod = yaml.load(f_r, Loader=yaml.FullLoader)
            self.ev_mod = self.load_model(ev_mod)              # event model

    def load_model(self, mod):
        '''
        Loading the models
        ep5_v3 : segmentation model for 40x
        ep15_x20_otsu : segmentation model for 20x
        '''
        with open('modules/settings/models.yaml') as f_r:
            dic_mod = yaml.load(f_r, Loader=yaml.FullLoader)
        model_loaded = models.load_model(Path('models') / dic_mod[mod])
        return model_loaded
