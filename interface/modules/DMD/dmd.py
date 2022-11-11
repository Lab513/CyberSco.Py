'''
DMD
'''

from interface.flask_app import *
from interface.modules.misc_import import *

def sending_masks(debug=[]):
    '''
    Send the masks names
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


@socketio.on('image_canvas')
def save_png_for_DMD(b64):
    '''
    Save the base64 image as png image for DMD
    '''
    b64 = b64.split('base64,')[1]
    im = Image.open(BytesIO(base64.b64decode(b64)))
    im.save(opj('interface', 'static', 'dmd',
                f'{name_img_dmd}.png'), 'PNG')
    sending_masks()                    # refresh masks list
