'''
Handle the data
Deals with images, masks, preparation of the datasets for processing ..
Possibility to save the data with sava_data parameter.
By default, only the path is saved.
'''
import os
opb = os.path.basename
import cv2
from pathlib import Path
import numpy as np
from sklearn.model_selection import train_test_split
import modules_unet.images_enhance as ie

class HANDLE(object):

    def __init__(self, *all_dir, kind='train', format='tiff', dim=512, dil=0, flood=False):
        '''
        '''
        self.format = format
        self.lenf = len(self.format)
        self.dim = (dim, dim)
        self.dil = dil
        self.l0 = [ 6,30,55,60,91,93,94,105,112,116,119 ]
        #self.l1 = [ 121,141,142,153,154,155,176,178 ]
        if kind == 'train':
            self.dir_images, self.dir_masks = all_dir
            self.training_set_name = opb(self.dir_images)
            self.tab_images, self.tab_masks = [], []
            print('########## self.dir_images ', self.dir_images)
            self.addr_data = os.path.dirname(self.dir_images)
        elif kind == 'test':
            self.dir_test = all_dir[0]
            print("self.dir_test ", self.dir_test)
            self.tab_test_images, self.tab_files  = [], []
            self.load_test_im()

    def take_num(self, elem):
        '''
        Extract the index of the file : for example 3 in frame3.jpg
        '''
        print("### elem   ", elem)
        num = int(elem[:-5])
        return num

    def dilated_contour(self, img):
        '''
        '''
        if self.dil > 1:
            kernel = np.ones(( self.dil, self.dil ), np.uint8)
            img_out = cv2.dilate(img.copy(), kernel, iterations = 1)       # dilation
        else:
            img_out = img

        return img_out

    def use_flood_from_img_to_mask(self, mask, img):
        '''
        '''
        lod, upd = (8,)*4, (5,)*4
        img_interm = img.copy()
        # seed point is in the middle up..
        cv2.floodFill(img_interm, None, seedPoint=(250,10),\
                    newVal=(0,0,0) , loDiff=lod, upDiff=upd)
        mask[ img_interm == 0 ] = 0

    def flip_rand(self, img_r, img_mask, val):
        '''
        flip images and make random stuff
        '''
        img = cv2.flip(img_r, 0)
        img = ie.random_change(img)
        self.tab_images.append(img)
        img_m = cv2.flip(img_mask, 0)
        self.tab_masks.append(img_m)

    def init_with_rotate(self, angle):
        '''
        Beginning with rotation
        '''
        print(" Angle {}°".format(angle))
        ## image
        img_r = ie.rotateImage(self.img_orig, angle) # rotate image
        img = img_r.copy()
        img = ie.random_change(img)
        self.tab_images.append(img)
        ## mask
        img_mask = ie.rotateImage(self.img_mask_orig, angle) # rotate mask
        self.tab_masks.append(img_mask)
        return img_r, img_mask

    def apply_transformations(self, angle):
        '''
        Rotate, flip and random operations
        '''
        img_r, img_mask = self.init_with_rotate(angle)
        self.flip_rand(img_r, img_mask, 0)
        self.flip_rand(img_r, img_mask, 1)
        self.flip_rand(img_r, img_mask, -1)

    def resize(self,im):
        '''
        '''
        im = cv2.resize(im, self.dim, interpolation = cv2.INTER_AREA)
        return im

    def specific_flood_fill(self):
        '''
        '''
        if self.training_set_name == 'training-cell':          # flood fill for the specific training set : "training-cell"
            if self.num in self.l0:
                self.use_flood_from_img_to_mask(self.img_mask_orig, self.img_orig)

    def init_image_and_mask(self, file):
        '''
        Initialize image and mask
        '''
        addr_img = self.dir_images / file
        self.num = self.take_num(opb(str(addr_img)))
        self.img_orig = self.resize(cv2.imread(str(addr_img)))  # BF
        print('Creating and change {}'.format(addr_img))
        self.tab_images.append(self.img_orig)
        file_mask = self.dir_masks / file
        self.img_mask_orig = self.dilated_contour(self.resize(cv2.imread(str(file_mask), 0)))  # RFP
        self.specific_flood_fill()
        self.tab_masks.append(self.img_mask_orig)

    def show_tables(self):
        '''
        Debug function for verifying images and masks
        '''
        for id in range(len(self.tab_masks)):
            print(id)
            cv2.imshow('imageOpen', self.tab_images[id])
            cv2.imshow('maskOpen', self.tab_masks[id])
            cv2.waitKey(0)

    def make_training_and_test_dataset(self):
        '''
        Prepare training set and test datasets for the training process
        '''
        self.tab_images = np.array(self.tab_images, dtype = np.float32)/255
        self.tab_masks = np.array(self.tab_masks,  dtype = np.float32)[:, :, :]/255
        self.train_images, self.test_images, self.train_masks, self.test_masks = train_test_split(self.tab_images, self.tab_masks, test_size=0.05)
        del self.tab_images
        del self.tab_masks

    def prepare_images_and_masks(self, activate_ti, step_ang=60, show_table=False):
        '''
        '''
        for f in self.list_file:
            if f[-self.lenf:] == self.format:
                self.init_image_and_mask(f)
                if activate_ti :
                    for ang in range(0, 360, step_ang):
                        self.apply_transformations(ang)
        if show_table:
            self.show_tables()

    def check_path(self, path, create=False):
        '''
        Check if path exists
        If create True create this path
        '''
        if not os.path.isdir(path):
            if not create:
                quit("The directory {} doesn't exist !".format(path))
            else:
                os.mkdir(path)

    def check_existing_folders_and_files(self):
        '''
        '''
        p = Path('.')
        self.check_path( self.dir_images )
        self.check_path( self.dir_masks )
        self.check_path( p / 'models', create=True )
        self.check_path( p / 'predictions', create=True )

        self.list_file = os.listdir(self.dir_images)
        if self.list_file is None:
            quit("No file in {} !".format(self.dir_images))

    def load_test_im(self):
        '''
        Load images for tests
        '''
        for f in os.listdir(self.dir_test):
            if f[-self.lenf:] == self.format:
                img = self.resize(cv2.imread(str(self.dir_test / f)))
                self.tab_test_images.append(img)
                self.tab_files.append(f[:-self.lenf])
        self.tab_test_images = np.array(self.tab_test_images, dtype=np.float32)/255
