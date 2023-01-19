'''
image
'''

from PIL import Image, ImageFont, ImageDraw
import cv2

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


def insert_image_scale(addr_img, magnif, pos=(10, 480), debug=[]):
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
