import os
opb = os.path.basename
opd = os.path.dirname
from pathlib import Path
import cv2

class PREPARE_AFTER_PRED():
    '''
    Routines for processing after the prediction
    '''

    def take_num(self, elem):
        '''
        Extract the index of the file : for example 3 in frame3.jpg
        '''
        num = int(elem[:-4][5:])
        self.mess_curr_num(num)
        return num

    def make_addr_im_mask_event(self, im):
        '''
        '''
        try:
            self.addr_im_mask_event = self.dir_movie_pred_events  / im         # address events
        except:
            print('cannot produce self.addr_im_mask_event ')

    def read_mask_event(self):
        '''
        '''
        try:
            self.img_mask_event = cv2.imread( str(self.addr_im_mask_event), cv2.IMREAD_COLOR )   #  read mask event
        except:
            print('cannot produce self.img_mask_event ')

    def load_image_and_mask(self, im):
        '''
        Load image and mask
        '''
        self.addr_im_mask = self.dir_movie_pred  / im                          # address pred for seg
        self.make_addr_im_mask_event(im)
        self.addr_im = self.dir_movie_test  / (im[:-4] + '.tiff')              # address original image
        ##
        self.img_mask = cv2.imread( str(self.addr_im_mask), cv2.IMREAD_COLOR )   #  read mask
        self.read_mask_event()
        self.img = cv2.imread( str(self.addr_im), cv2.IMREAD_COLOR )             #  read image

    def mess_curr_num(self, num):
        '''
        '''
        print('############################ ')
        print('#######################  self.num is ', num)
        print('############################ ')

    def settings_after_main_seg_pred(self):
        '''
        Addresses for the predictions, seg and events
        '''
        list_pred = os.listdir(os.path.join('predictions','movie'))
        for p in list_pred:
            if 'ep' in p:
                self.pred_dir_imgs = p
                self.dir_movie_pred = Path('predictions') / 'movie' / f'{p}'
            elif 'buds' in p:
                if len(list_pred) == 1:
                    self.pred_dir_imgs = p
                    self.dir_movie_pred = Path('predictions') / 'movie' / f'{p}'
                else:
                    self.pred_dir_events = p
                    self.dir_movie_pred_events = Path('predictions') / 'movie' / f'{p}'
        #dicomm0 = { 'dir_seg' : self.pred_dir_imgs, 'dir_events' : self.pred_dir_events } #
        #self.dir_movie_pred = Path('predictions') / 'movie' / '{dir_seg}'.format(**dicomm0)
        #self.dir_movie_pred_events = Path('predictions') / 'movie' / '{dir_events}'.format(**dicomm0)
        self.dir_movie_test = Path('test') / 'movie'
        #
        self.iter = 0
        self.currframe = 0
        self.settings_from_options()

    def settings_from_options(self):
        '''
        Settings
        '''
        self.kind = ''
        if self.thresh_after_pred: self.thresh = '_th' + str(self.thresh_after_pred)
        else: self.thresh = ''
