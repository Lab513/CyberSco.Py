'''
Camera imported in CyberSco.py..
Choice between Evolve512 or Zyla camera
'''

from colorama import Fore, Style         # Color in the Terminal
from PIL import Image, ImageFont, ImageDraw
from flask import Flask, Response, request, redirect
import shutil as sh
import socket
import yaml
import cv2
import os
op = os.path
opd, opb, opj, ope = op.dirname, op.basename, op.join, op.exists

try:
    from devices.Evolve512 import EVOLVE as EV
    from devices.Zyla import ZYLA as ZY
    from track_segm.cam_pred import CAM_PRED
except:
    from modules.devices.Evolve512 import EVOLVE as EV
    from modules.devices.Zyla import ZYLA as ZY
    from modules.track_segm.cam_pred import CAM_PRED

app = Flask(__name__)

# camera in use Evolv or Zyla
with open('interface/settings/cam_used.yaml') as f_r:
    cam_used = yaml.load(f_r, Loader=yaml.FullLoader)

if cam_used == 'Evolv':       # use the Evolve camera
    cam = EV()
elif cam_used == 'Zyla':      # use the Zyla camera
    cam = ZY()

static = opj(os.getcwd(), 'interface', 'static')
addr_pic = opj(static, 'curr_pic', 'frame0.png')
addr_curr_pic = opj(static, 'curr_pic')
if not os.path.exists(addr_curr_pic):
    os.mkdir(addr_curr_pic)
addr_pic_read = addr_pic
mda_pic_addr = opj(static, 'mda_pics')
mda_imgs_pos = opj(static, 'mda_pics', 'imgs_pos')
if not os.path.exists(mda_pic_addr):
    os.mkdir(mda_pic_addr)
if not os.path.exists(mda_imgs_pos):
    os.mkdir(mda_imgs_pos)

livecam = True
# exposure time
exp_time = 200

# make prediction and find contours
cp = CAM_PRED(mda_pic_addr, mode='live')


@app.route('/')
def index():
    return "Default Message"

@app.route('/magnif', methods = ['POST'])
def receive_magnif():
    '''
    Retrieve magnification for size bar..
    '''
    global magnif
    if request.method == 'POST':
        magnif = request.form.get('magnif')
        print(f'the current magnification is {magnif}')

    return "Default Message"


@app.route('/exp_time', methods = ['POST'])
def receive_exp_time():
    '''
    Retrieve exposure time
    '''
    global exp_time
    if request.method == 'POST':
        new_exp_time = request.form.get('exp_time')
        print(f'new exp time is {new_exp_time}')
        exp_time = int(new_exp_time)

    return "Default Message"


@app.route('/autocontrast', methods = ['POST'])
def receive_autocontrast():
    '''
    Retrieve autocontrast
    '''
    if request.method == 'POST':
        new_autoc = request.form.get('val')
        print(f'new autocontrast is {new_autoc}')
        if new_autoc == 'true':
            cam.autocontrast = True
        else:
            cam.autocontrast = False

    return "Default Message"


@app.route('/quit_live')
def quit_live():
    '''
    Quit the live mode before switching to MDA mode..
    '''
    print('Closing the server for live camera !!!')
    cam.close()
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


@app.route('/imgs_pos')
def imgs_pos():
    '''
    '''
    cam.close()
    global addr_pic_read
    addr_pic_read = opj(mda_imgs_pos, 'frame0.png')
    print(f"########### changed addr_pic_read {addr_pic_read} ")
    livecam = False
    return addr_pic_read


def copy_pic_in_mda(debug=[]):
    '''
    copy in static/mda_pics
    '''
    if 1 in debug:
        print('copy in static/mda_pics')
    sh.copy(addr_pic, mda_pic_addr)
    addr_copy = opj(mda_pic_addr, opb(addr_pic))
    im = Image.open(addr_copy)
    if 2 in debug:
        print(f'## addr_copy is {addr_copy}')
    im.save(addr_copy[:-4] + '.tiff', 'TIFF')


def adapt_size(addr_pic, debug=[]):
    '''
    Adapt image size for predictions
    '''
    img = cv2.imread(addr_pic)
    res = cv2.resize(img, dsize=(512, 512), interpolation=cv2.INTER_CUBIC)
    cv2.imwrite(addr_pic, res)
    lap = laplacian_var(res)
    if 0 in debug:
        print(f'************* Laplacian value is {lap} ************')


def insert_scale_bar(addr_img, pos, h=4, w=50,
                     thick=-1, col=(255, 255, 255), debug=[]):
    '''
    Bar for indicating the size
    '''
    img = cv2.imread(addr_img)
    p0, p1 = pos[0]+10, pos[1]+10                           # bar position
    # p0, p1 = 0,0
    cv2.rectangle(img, (p0, p1), (p0+w, p1-h), col, thick)     # scale bar
    cv2.imwrite(addr_img, img)


def insert_text(addr_img, text, size=0.4, pos=None, debug=[]):
    '''
    Insert text in image
    '''
    img = Image.open(addr_img)
    font = ImageFont.truetype("arial",14)
    draw = ImageDraw.Draw(img)
    p0, p1 = pos[0]+20, pos[1]-20
    draw.text((p0,p1), text, font=font, fill='#fff')
    img.save(addr_img)


def insert_image_scale(addr_img, pos=(10, 480), debug=[]):
    '''
    Insert the scale of the image for the current objective in use
    '''
    # dictionary magnification <--> size in µm
    dic_scale = {'20x': '30µm', '40x': '15µm',
                 '60x': '10µm', '100x': '6µm'}
    size_scale = dic_scale[magnif]
    # scale bar with the value in µm
    insert_text(addr_img, size_scale, pos=pos) # text, size in µm
    insert_scale_bar(addr_img, pos) # rectangle


def laplacian_var(img):
    '''
    Variance of the image's Laplacian
    '''
    img = cv2.GaussianBlur(img, (3, 3), 0)
    src_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    kernel_size = 3
    return cv2.Laplacian(src_gray, cv2.CV_16S, ksize=kernel_size).var()


def gen(predict=True, debug=[]):
    while True:
        if livecam:
            # try:
            if 0 in debug:
                print(f'exp_time is {exp_time}')
            if 1 in debug:
                print('...')
            # take a new img
            cam.take_pic(addr_pic, exp_time=exp_time, allow_contrast=True)
            adapt_size(addr_pic)
            insert_image_scale(addr_pic)
            # copy image for making predictions on it after
            copy_pic_in_mda()
            # except:
            #     print('Cannot copy to mda folder')
            #     print('Check if the camera is on !!!')
            if predict:
                try:
                    cp.predict_and_save()   # predict in real time
                except:
                    print('Cannot predict')
            if 1 in debug:
                print("took pic")
        try:

            if 2 in debug:
                print(f"addr_pic_read {addr_pic_read}")
            if ope(addr_pic_read):
                img = cv2.imread(addr_pic_read)
                _, jpeg = cv2.imencode('.jpg', img)
                frame = jpeg.tobytes()
                # return current frame
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        except:
            print('Cannot provide a frame !!')


def message_at_beginning(host, port, debug_addr_server=False):
    '''
    '''
    print(Fore.GREEN + """
                ***********************************

                            Camera

                ***********************************
    """)


    if debug_addr_server:
        print(f'address: {host}:{port}')


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    ip = socket.gethostbyname(socket.gethostname())
    PORT = 2204
    HOST = ip
    message_at_beginning(HOST,PORT)
    print(Style.RESET_ALL)
    # remove FLask messages
    app.env = "development"
    app.run(host=HOST, port=PORT, threaded=True)
