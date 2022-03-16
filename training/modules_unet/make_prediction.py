#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on Tue Mar 24 14:44:40 2020

@author: Williams modified by Lionel 2/7/2020
python make_prediction.py -m modelname -t testname
"""

import os
from pathlib import Path
import numpy as np
import cv2
from tensorflow.keras import models
# utilities
from .util import UTIL
# handle images
from .handle_images import HANDLE

ut = UTIL()
p = Path('models')
dir_test_images = Path('test') / ut.args.test
ha = HANDLE(dir_test_images, kind='test', dim=512)

model_trained = p / ut.args.model #
print('##### model_trained is ' + str(model_trained))
my_model = models.load_model(model_trained)
ut.make_predict_subdir(ha)    # subdir for the predictions

for i,test_im in enumerate(ha.tab_test_images):
    prediction = my_model.predict(np.array([test_im]))
    ut.save_prediction(i,prediction)

print('########  Predictions done')
