'''
DMD
'''

import base64
from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.init.init_devices import *
from modules.modules_mda.positions import POS

ldevices = [ol, pr, None, co, xc, ga, se]
pos = POS(ldevices)


def sending_masks(debug=[]):
    '''
    Send the masks names for refreshing the list in the interface
    '''
    if 0 in debug:
        print('sending the masks')
    dmd_path = Path('interface') / 'static' / 'dmd'
    list_png = [opb(str(add)) for add in list(dmd_path.glob('*.png'))]
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


def try_create_dmd_folder(dmd):
    '''
    Create the DMD folder if it does not exist..
    '''
    if not os.path.exists(dmd):
        os.mkdir(dmd)


@socketio.on('image_canvas')
def save_png_for_DMD(b64):
    '''
    Save the base64 image as png image for DMD
    '''
    b64 = b64.split('base64,')[1]
    decoded = base64.b64decode(b64)
    path_dmd = opj('interface', 'static', 'dmd')
    try_create_dmd_folder(path_dmd)
    img_addr = opj(path_dmd, f'{name_img_dmd}.png')
    with open(img_addr, 'wb') as fb:
        fb.write(decoded)
    # refresh masks list
    sending_masks()


def make_DMD_test(name_img_test):
    '''
    Perform the DMD acquisition
    '''
    # filt, kind_fluo = pos.define_filt_kind_with_name(dic_chan)
    xc.set_intens_level(1)
    # set the filter for the fluo with Xcite
    ol.set_wheel_filter(5)
    # close the BF
    ol.set_shutter(shut='off')

    mask_exp_time = 5

    pos.trigger_dmd_image(name_img_test, mask_exp_time)
    sleep(5)                     # delay for loading and triggering
    print('shut Xcite on')
    xc.shut_on()
    sleep(2)
    ##
    addr_pic = 'interface/static/curr_pic/frame0.png'    # snap BF
    addr_snap = 'interface/static/snapped/snap_curr.png'
    sh.copy(addr_pic, addr_snap)

    # stop using the Xcite
    sleep(int(mask_exp_time))
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


@socketio.on('infos_DMD_test')
def test_DMD(infos_dmd):
    '''
    test the DMD
    '''
    infd = infos_dmd.split('&')
    name_img_test = infd[0]
    name_SC = infd[1]
    path_dmd = opj('interface', 'static', 'dmd')
    img_addr = opj(path_dmd, f'{name_img_test}.png')
    print(f'addr img for DMD is { img_addr }')
    print(f'using Setting Channels { name_SC }')

    make_DMD_test(name_img_test)
