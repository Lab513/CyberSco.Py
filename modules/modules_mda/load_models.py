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

    def load_used_models(self):
        '''
        Load the list of models used and load them
        '''
        with open('modules/settings/used_models.yaml') as f_r:
            used_models = yaml.load(f_r, Loader=yaml.FullLoader)
            self.mod0 = self.load_model(used_models['mod0']['id'])        # main model
            self.mod1 = self.load_model(used_models['mod1']['id'])

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
