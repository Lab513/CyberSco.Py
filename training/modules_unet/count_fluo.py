# -*- coding: utf-8 -*-
"""
@author:    Williams BRETT
@date:      13-11-2019
@brief:     this is a simple code to detect spot in a fluorescence image (here, RPF)
modified by Lionel 22-7-2020
"""

import cv2
import numpy as np
import os
from pathlib import Path
from matplotlib import pyplot as plt

class COUNT_FLUO():
    '''
    '''
    def __init__(self):
        self.list_nb_cells = []

    def bytescaling(self, data, cmin=None, cmax=None, high=255, low=0):
        '''
        '''
        if data.dtype == np.uint8:
            return data
        if high > 255:
            high = 255
        if low < 0:
            low = 0
        if high < low:
            raise ValueError("`high` should be greater than or equal to `low`.")
        if cmin is None:
            cmin = data.min()
        if cmax is None:
            cmax = data.max()
        cscale = cmax - cmin
        if cscale == 0:
            cscale = 1
        scale = float(high - low) / cscale ; bytedata = (data - cmin) * scale + low
        return (bytedata.astype(np.uint8))

    def variance_of_laplacian(self, image):
        '''
        '''
        if image is None:
            print ('Erreur: opening image')
            return -1
        image = cv2.cvtColor(image,cv2.COLOR_GRAY2BGR)
        image = cv2.GaussianBlur(image, (3, 3), 0)
        src_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        kernel_size = 3
        return cv2.Laplacian(src_gray, cv2.CV_16S, ksize=kernel_size).var()

    def filter2D(self,img):
        '''
        '''
        kernel = np.array((
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, 24, -1, -1],
            [-1, -1, -1, -1, -1],
            [-1, -1, -1, -1, -1]), dtype="int")
        img = cv2.filter2D(img, -1, kernel)
        return img

    def count_cells(self, addrfluo):
        '''
        '''
        img  = cv2.imread( str(addrfluo), 0 )      # cv2.IMREAD_UNCHANGED
        img = self.bytescaling(img)
        img = cv2.GaussianBlur(img,(5,5),0)
        img = self.filter2D(img) # filtering with kernel..
        ret2, th2 = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        self.contours, hierarchy = cv2.findContours(th2.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        self.list_nb_cells += [len(self.contours)]                        # number of cells found with OTSU
