#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from modules_unet.util import UTIL

## Deep Learning
import modules_unet.model_unet as model_unet
from tensorflow.keras import models

## handle images
from modules_unet.handle_images import HANDLE

print("""
Created on Sat Mar 21 14:52:24 2020
@author: Williams modified by Lionel July 2nd 2020
@script: train_unet.py - UNET segmentation with Tensorflow Keras
Syntax example :
    * python train_unet.py -d name_of_the_training_set_in_the_folder_training_sets
Description:
The model is saved with the code in the folder "models"

""")

#"ep5_dil3":"training-cell-ep5-bs4-dil3-fl_date06-08-2020-11-26",
#ep5_dil3":"training-cell_v2-ep5-bs4-dil3-fl_date04-10-2020-11-25  training-cell_v2

# True False
activate_ti = True   # Transformations activated
epochs = 15          # nb of epochs
batch_size = 4       # nb of pics per batch
dim = 512            # size of the pictures
dil = 1              # dilate the prediction
flood = False        # clean the background

ut = UTIL()
p = Path('training_sets')
try:
    root = p / ut.args.data #
except:
    ut.error_missing_option_data()

ha = HANDLE( root / 'images', root / 'masks', dim=dim, dil=dil, flood=flood )
ha.check_existing_folders_and_files()
ha.prepare_images_and_masks(activate_ti, step_ang=60)

if True:
    ut.init_time()
    ha.make_training_and_test_dataset()
    my_model = model_unet.model(64, dim, dim)
    my_model.compile(optimizer='adam',
                     loss='binary_crossentropy',
                     metrics=['accuracy'])

    my_model.fit(ha.train_images,
                 ha.train_masks,
                 epochs = epochs,
                 batch_size = batch_size,
                 validation_data = (ha.test_images, ha.test_masks))
    ut.make_savings(ha, models, my_model, epochs, batch_size, dil, flood)

print("""
Finished
""")
