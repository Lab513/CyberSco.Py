'''
DMD
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
from modules.modules_mda.positions import POS
import cv2
import yaml
import numpy as np
import base64

ldevices = [ol, pr, None, co, xc, ga, se]
pos = POS(ldevices)


def sending_masks(debug=[]):
    '''
    Send the masks names for refreshing the list in the interface
    '''
    if 0 in debug:
        print('sending the masks')
    dmd_path_masks = Path('interface') / 'static' / 'dmd' / 'masks'
    list_png = [opb(str(add)) for add in list(dmd_path_masks.glob('*.png'))]
    list_dmd_pics = [im_png[:-4] for im_png in list_png]
    if 1 in debug:
        print(f'list_dmd_pics is {list_dmd_pics}')
    str_list_dmd_pics = json.dumps(list_dmd_pics)
    emit('dmd_masks', f'{str_list_dmd_pics}', broadcast=True)


@socketio.on('name_img_mosaic')
def name_img_DMD(name_img_mosaic):
    '''
    Name for DMD image
    '''
    global name_img_dmd
    name_img_dmd = name_img_mosaic


def try_create_dmd_folder(path):
    '''
    Create the DMD folder if it does not exist..
    '''
    if not os.path.exists(path):
        os.makedirs(path)


@socketio.on('image_canvas')
def save_png_for_DMD(b64):
    '''
    Save the base64 image as png image for DMD
    '''
    b64 = b64.split('base64,')[1]
    decoded = base64.b64decode(b64)
    path_dmd_masks = opj('interface', 'static', 'dmd', 'masks')
    try_create_dmd_folder(path_dmd_masks)
    path_dmd_illum = opj('interface', 'static', 'dmd', 'illum')
    try_create_dmd_folder(path_dmd_illum)
    path_dmd_illum = opj('interface', 'static', 'dmd', 'img_calib')
    try_create_dmd_folder(path_dmd_illum)
    img_addr = opj(path_dmd_masks, f'{name_img_dmd}.png')
    with open(img_addr, 'wb') as fb:
        fb.write(decoded)
    # refresh masks list
    sending_masks()


def closing_devices_after_test():
    '''
    acquisition is finished
     return to initial state..
    '''
    # return to 0 and shut off
    xc.set_intens_level(0)
    sleep(pos.delay_xcite)
    xc.shut_off()
    sleep(pos.delay_xcite)
    print('Normally intensity is 0 and shutter off !!!')
    ol.set_wheel_filter(1) # return to BF
    print('wheel filter to BF')
    ol.set_shutter(shut='on')
    print('microscope shutter on..')


def dmd_retrieve_SC(name_SC, debug=[]):
    '''
    '''
    addr_SC = f'interface/settings/settings_channels/{name_SC}.yaml'
    if 1 in debug:
        print(f'addr_SC is {addr_SC} ')
    with open(addr_SC) as f_r:                           # current SC
        # Settings channels dictionary
        dic_chan = yaml.load(f_r, Loader=yaml.FullLoader)

    return dic_chan


def init_for_DMD_test(name_SC):
    '''
    '''
    dic_chan = dmd_retrieve_SC(name_SC)
    filt = int(dic_chan['filter'])
    xcite_intens = dic_chan['Xcite']
    # filt, kind_fluo = pos.define_filt_kind_with_name(dic_chan)
    xc.set_intens_level(xcite_intens)
    # set the filter for the fluo with Xcite
    ol.set_wheel_filter(filt)
    # close the BF
    ol.set_shutter(shut='off')


def dmd_move_images():
    '''
    '''
    addr_pic = 'interface/static/curr_pic/frame0.png'    # snap BF
    addr_snap = 'interface/static/snapped/snap_curr.png'
    addr_dmd_illum = 'interface/static/dmd/illum/curr_dmd.png'
    sh.copy(addr_pic, addr_snap)
    sh.copy(addr_pic, addr_dmd_illum)


def make_DMD_test(name_img_test, name_SC, debug=[]):
    '''
    Perform the DMD acquisition
    '''
    init_for_DMD_test(name_SC)

    mask_exp_time = 5

    # apply calibration to image..
    apply_calib(name_img_test)
    pos.trigger_dmd_image(name_img_test,mask_exp_time)

    sleep(5)                     # delay for loading and triggering
    print('shut Xcite on')
    xc.shut_on()
    sleep(2)
    ##
    dmd_move_images()

    if name_img_test == 'calib':
        make_calib()
    # stop using the Xcite
    sleep(int(mask_exp_time))
    closing_devices_after_test()


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
    # try:

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
    # except:
    #     print('Cannot apply calibration..')


@socketio.on('infos_DMD_test')
def test_DMD(infos_dmd):
    '''
    test the DMD
    '''
    infd = infos_dmd.split('&')
    name_img_test = infd[0]
    name_SC = infd[1]
    path_dmd = opj('interface', 'static', 'dmd', 'masks')
    img_addr = opj(path_dmd, f'{name_img_test}.png')
    print(f'addr img for DMD is { img_addr }')
    print(f'using Setting Channels { name_SC }')

    make_DMD_test(name_img_test, name_SC)
