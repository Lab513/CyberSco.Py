import cv2
import yaml
import numpy as np



def find_coord_pts(img):
    '''
    Find coordinates of the shapes
    '''
    lpts = []
    ret, thr = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    cntrs, _ = cv2.findContours(thr,
                                cv2.RETR_TREE,
                                cv2.CHAIN_APPROX_SIMPLE)[-2:]
    new_img = np.zeros((img.shape))
    for c in cntrs:
        if cv2.contourArea(c) > 100:
            new_img = cv2.drawContours(new_img, [c], -1, (255, 255, 255), -1)
            x, y, w, h = cv2.boundingRect(c)
            lpts.append([x,y])
    print(lpts)
    return lpts


def make_calib():
    '''
    DMD calibration
    '''
    addr_dmd_mask_calib = 'interface/static/dmd/masks/calib.png'
    addr_dmd_illum_calib = 'interface/static/dmd/illum/curr_dmd.png'
    img_in = cv2.imread(addr_dmd_mask_calib,0)
    img_out = cv2.imread(addr_dmd_illum_calib,0)
    # coordinates of the projected image
    l0 = find_coord_pts(img_in)
    # coordinates of the initial image
    l1 = find_coord_pts(img_out)
    # save the calibration data
    with open('interface/static/dmd/calib.yaml', "w") as f_w:
        yaml.dump([l0,l1], f_w)


def apply_calib(name_img_test):
    '''
    Transform the image from Drawer.js.
    '''

    with open('interface/static/dmd/calib.yaml') as f_r:
        lcal = yaml.load(f_r, Loader=yaml.FullLoader)
    lpts0 = np.float32(lcal[0])
    lpts1 = np.float32(lcal[1])
    # find the Transform
    M = cv2.getAffineTransform(lpts1,lpts0)
    #
    addr_test = f'interface/static/dmd/masks/{name_img_test}.png'
    img_test = cv2.imread(addr_test,0)
    rows,cols = img_test.shape
    if name_img_test != 'calib':
        # Apply the affine Transform
        dst = cv2.warpAffine(img_test,M,(cols,rows))
    else:
        # no transformation if calibration image
        dst = img_test
    addr_img_calib = f'interface/static/dmd/img_calib/{name_img_test}.png'
    cv2.imwrite(addr_img_calib, dst)
    print('Applied calibration.. ')
