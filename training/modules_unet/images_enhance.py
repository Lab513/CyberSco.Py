import cv2
import numpy as np
import random

randi = random.randint

def zoom(img, fact):
    '''
    fact : zoom factor in a windows reduced
    of the same factor from original windows,
    which is centered in the pic
    '''
    h, w, c = img.shape
    posh, dh = int(h/2), int(h/(2*fact))
    posw, dw = int(w/2), int(w/(2*fact))
    crop_img = img[ posh-dh:posh+dh, posw-dw:posw+dw ]
    img = cv2.resize(crop_img, (512,512), interpolation = cv2.INTER_CUBIC)
    return img

def rotateImage(img, ang):
    img_center = tuple(np.array(img.shape[1::-1])/2)
    rot_mat = cv2.getRotationMatrix2D(img_center, ang, 1.0)
    result = cv2.warpAffine(img, rot_mat, img.shape[1::-1], flags=cv2.INTER_LINEAR)
    return result

def bruit(img):
    h, w, c = img.shape
    n = np.random.randn(h, w, c)*randi(5, 30)
    return np.clip(img+n, 0, 255).astype(np.uint8)

def change_gamma(img, alpha=1.0, beta=0.0):
    return np.clip(alpha*img+beta, 0, 255).astype(np.uint8)

def color(img, alpha=20):
    n =  [randi(-alpha, alpha) for i in range(3)]
    return np.clip(img+n, 0, 255).astype(np.uint8)

def random_change(img):
    if randi(0,1):
        img = change_gamma(img, random.uniform(0.8, 1.2), np.random.randint(100)-50)
    if randi(0,1):
        img = bruit(img)
    if randi(0,1):
        img = color(img)
    # if randi(0,1):
    #     img = zoom(img,1+0.3*np.abs(np.random.randn()))
    return img
