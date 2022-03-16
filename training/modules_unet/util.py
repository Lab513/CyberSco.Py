'''
Utilities..
If "save_data" in save_experim is set True the dataset is saved,
otherwise only the path is saved.
'''
import os
import shutil as sh
from colorama import Fore, Back, Style
from datetime import datetime
from time import time
import argparse
from pathlib import Path
import cv2
import json
import numpy as np
import tensorflow as tf
from tensorflow.python.client import device_lib

class UTIL(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='train with u-net')
        parser.add_argument('-d', '--data', type=str, help='dataset eg : training-cell')
        parser.add_argument('-m', '--model', type=str, help='model trained')
        parser.add_argument('-n', '--net', type=str, help='net used for training')
        parser.add_argument('-o', '--output', type=str, help='destination')
        parser.add_argument('-t', '--test', type=str, help='test for predictions')
        parser.add_argument('-f', '--file', type=str, help='file on which are made predictions')
        self.args = parser.parse_args()

    def init_time(self):
        '''
        Trigger the chronometer
        '''
        self.t0 = time()

    def date(self):
        '''
        Return a string with day, month, year, Hour and Minute..
        '''
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M")
        return dt_string

    def show_time_calc(self):
        '''
        Show time elapsed since chronometer was triggered
        '''
        t1 = time()
        sec = round(((t1-self.t0)%60))
        min = (t1-self.t0)//60
        print('calculation time is {0} min {1} sec '.format(min,sec))

    def save_experim(self, ha, save_data=False):
        '''
        Save all the code for training with the resulting model and dataset
        '''
        sh.copytree('modules_unet', self.rep_save_exp / 'modules_unet')
        if save_data:
            name_data = os.path.basename(ha.addr_data)
            sh.copytree(ha.addr_data, self.rep_save_exp / name_data)
        else:
            with open(self.rep_save_exp / 'data_path.txt','w') as f:
                f.write(ha.addr_data)
        sh.copy('train_unet.py', self.rep_save_exp)

    def get_computing_infos(self):
        '''
        '''
        try:
            dl = device_lib.list_local_devices()[2]
            gpu_id = dl.physical_device_desc
            gpu_mem = str(round(int(dl.memory_limit)/1e9,2)) + ' MB'
            self.soft_hard_infos = { 'id': gpu_id, 'mem': gpu_mem, 'tf_version': tf.__version__ }
        except:
            print('issue with computing_infos')

    def save_computing_infos(self):
        '''
        Save computing informations about the training..
        '''
        self.get_computing_infos()
        with open(self.rep_save_exp / 'computing_infos.txt','w') as f:
            json.dump(self.soft_hard_infos, f)

    def save_training_history(self, my_model):
        '''
        Save the training history
        '''
        hist = my_model.history
        # print(hist.params)
        with open(self.rep_save_exp / 'training_history.json','w') as f:
            json.dump(hist.history, f)

    def error_missing_option_data(self):
        '''
        Alert if missing training dataset..
        '''
        print(Style.BRIGHT)
        print(Fore.RED + '## Need a dataset address for training: "--data address" ..')
        print(Style.RESET_ALL)

    def make_model_name(self, dil, flood, dic_proc_name):
        '''
        Make the name of the model
        '''
        name_proc0 = '{name}-ep{epochs}-bs{batch_size}'
        if dil > 1 : name_proc0 += '-dil{dilation}'
        if flood  : name_proc0 += '-fl'
        name_proc1 = name_proc0 + '_date{date}'
        name_proc = name_proc1.format(**dic_proc_name)
        return name_proc

    def make_savings(self, ha, models, my_model, epochs, batch_size, dil, flood):
        '''
        Save the model and the informations around the experiment.
        '''
        dic_proc_name = {'name': self.args.data,
                         'epochs': epochs,
                         'batch_size': batch_size,
                         'dilation': dil,
                         'date': self.date()}
        name_proc = self.make_model_name( dil, flood, dic_proc_name )
        print('name_proc ', name_proc)
        self.show_time_calc()
        dest = Path('models') / name_proc #self.args.output
        print('saving at address : {0} '.format(dest))
        self.rep_save_exp = dest / 'experiment'
        models.save_model( my_model, dest )
        self.save_experim(ha)
        self.save_computing_infos()
        self.save_training_history(my_model)

    def inverted_models_name_dic(self, model):
        '''
        Invert mapping between long models name and models shortcuts
        '''
        addr_models_json = str( Path('modules_unet')/'models.json' )
        with open(addr_models_json, "r") as f:
            models = json.load(f)
        self.inverted_models = dict(map(reversed, models.items()))
        try:
            shortcut = self.inverted_models[model]
        except:
            shortcut = model  # in case shortcut does not exist..
        return shortcut

    def make_predict_subdir(self, ha):
        '''
        Make sub directory for prediction
        '''
        self.ha = ha
        p = Path('./predictions')
        if self.args.test == 'movie':
            pred_date = 'movie'
        else:
            pred_date = 'predict_' + self.date()
        path_pred = p / pred_date                       # path for the predictions
        print("## prediction path is {0} ".format(path_pred))
        if not os.path.exists(path_pred):
            os.mkdir(path_pred)                                            # folder movie for pedictions
        short_model = self.inverted_models_name_dic(str(self.args.model))
        suff = str(self.args.test) + '_' + self.args.file + '_' + self.date()
        self.path_pred_model = path_pred / ( short_model + '_test_' + suff )    # address of the prediction

        os.mkdir(self.path_pred_model)

    def save_prediction(self, i, prediction):
        '''
        Save the prediction
        '''
        mask = prediction[0]*255
        addr_im_predicted = self.path_pred_model / (str(self.ha.tab_files[i]) + "png")
        print(addr_im_predicted)
        cv2.imwrite(str(addr_im_predicted), mask)
