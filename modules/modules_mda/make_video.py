'''
Make video
'''
from itertools import chain
from skimage import io
import numpy as np
import cv2
import glob
import re
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename


class MAKE_VIDEO():
    '''
    Create video from bunch of images
    '''

    def __init__(self):
        '''
        '''

    def take_num_frame_png(self, elem):
        '''
        for png pictures
        '''
        return int(re.findall('\d+', opb(elem)[:-4].split('_t')[1])[0])

    def draw_buds_segm_cntrs(self, images_sum, rep):
        '''
        '''
        for l in self.list_buds_hist_rep[rep]:
            # save mask of the segmentation
            cv2.drawContours(images_sum, [l[1]], -1, (255, 255, 255), 1)

    def make_superp_bf_rfp(self, addr_img_bf, frame_regexp, debug=[]):
        '''
        Superimposition BF RFP
        '''
        if 2 in debug:
            print(f'addr_img_bf is {addr_img_bf} ')
        img_bf = cv2.imread(addr_img_bf)

        try:
            addr_fluo = re.sub(frame_regexp, r'\1\2_rfp_t\3', addr_img_bf)
            img_fluo = cv2.imread(addr_fluo)
            # add fluo on BF
            images_sum = cv2.addWeighted(img_bf, 0.9, img_fluo, 0.5, 0)

        except:
            images_sum = img_bf
        addr_bf_fluo = re.sub(frame_regexp,
                    r'\1superp_bf_fluo_\2_t\3', addr_img_bf)
        # save superimposed pictures
        cv2.imwrite(addr_bf_fluo, images_sum)
        if 3 in debug:
            print(f'saved addr_fluo : {addr_fluo} ')
        return images_sum

    def make_superp_with_buds_segm(self, addr_img_bf,
                                   rep, images_sum,
                                   frame_regexp, debug=[]):
        '''
        Superimposition with size filtered buds
        '''
        # draw the buds (size filtered) contours on superimposed pics
        self.draw_buds_segm_cntrs(images_sum, rep)
        addr_bf_fluo_buds = re.sub(frame_regexp,
                                   r'\1superp_with_buds_\2_t\3',
                                   addr_img_bf)
        cv2.imwrite(addr_bf_fluo_buds, images_sum)
        if 3 in debug:
            print(f'saved addr_bf_fluo_buds : {addr_bf_fluo_buds}  ')

    def make_superp_and_buds(self, addr_img_bf, rep, debug=[]):
        '''
        '''
        frame_regexp = r'(.*\\)(frame\d+)_t(\d+.png)'
        images_sum = self.make_superp_bf_rfp(addr_img_bf, frame_regexp)
        ##### buds
        self.make_superp_with_buds_segm(addr_img_bf, rep,
                                        images_sum, frame_regexp)

    def image_fusion_for_BF_fluo(self, name_folder, debug=[]):
        '''
        Fusion BF and fluo when same iteration number
        Superposition RFP BF
        '''
        if 0 in debug: print(f'############## In image_fusion_for_BF_fluo')
        folder = opj(self.dir_mda_temp, name_folder)
        ll = [f for f in glob.glob(opj(folder,
                                   f'*{self.num}_t*.png'))
              if not re.match(r'.*superp_.*', f)]
        if 1 in debug:
            print(f'll is {ll} ')
        for rep, addr_img_bf in enumerate(ll):
            if 2 in debug:
                print(f'addr_img_bf is {addr_img_bf} ')
            self.make_superp_and_buds(addr_img_bf, rep)

    def make_list_imgs_for_video(self, prefix='',
                                 suffix='',
                                 name_folder='imgs_for_videos',
                                 debug=[]):
        '''
        List of images for the video
        '''
        folder = opj(self.dir_mda_temp, name_folder)
        if name_folder == 'imgs_for_BF_RFP_videos':
            # make fusions between fluo and BF
            self.image_fusion_for_BF_fluo(name_folder)

        ll = glob.glob(opj(folder, f'*{prefix}{self.num}{suffix}_t*.png'))
        # sorted list
        list_imgs_sorted = sorted(ll,
                                  key=lambda elem:
                                  self.take_num_frame_png(elem))
        if 1 in debug:
            print(f'## ll is {ll}')
            print(f'## list_imgs_sorted is {list_imgs_sorted}')
        self.list_imgs_vid = []
        for f in list_imgs_sorted:
            img = cv2.imread(opj(folder, f))
            self.list_imgs_vid.append(img)
        if 1 in debug:
            print(f'## self.list_imgs_vid is {self.list_imgs_vid}')

    def prepare_list_for_composite_vid(self, name_folder, debug=[1]):
        '''
        Prepare the list for the composite video
        '''
        folder = opj(self.dir_mda_temp, name_folder)
        ll0 = sorted(glob.glob(opj(folder,
                     f'frame{self.num}_t*.tiff')),
                     key=lambda elem: self.take_num_frame_png(elem))
        ll1 = sorted(glob.glob(opj(folder,
                     f'frame{self.num}_rfp_t*.tiff')),
                     key=lambda elem: self.take_num_frame_png(elem))
        ll2 = sorted(glob.glob(opj(folder,
                     f'frame{self.num}_gfp_t*.tiff')),
                     key=lambda elem: self.take_num_frame_png(elem))
        self.list_imgs_sorted = list(chain(*zip(ll0, ll1, ll2)))
        if 1 in debug:
            print(f'## self.list_imgs_sorted[:9] {self.list_imgs_sorted[:9]}')

    def make_list_imgs_for_composite_video(self,
                                           name_folder='.',
                                           debug=[1, 2]):
        '''
        List of images for the video
        '''
        if 1 in debug:
            print('#### making composite film !!!')
        self.prepare_list_for_composite_vid(name_folder)
        self.list_imgs_vid = []
        for f in self.list_imgs_sorted:
            img = cv2.imread(opj(self.dir_mda_temp, f))
            self.list_imgs_vid.append(img)
        if 2 in debug:
            print(f'## self.list_imgs_vid is {self.list_imgs_vid}')

    def make_vid_avi(self, prefix='', suffix='',
                     name_folder='', name_movie=''):
        '''
        Make video with avi format
        '''
        # make sorted list
        self.make_list_imgs_for_video(prefix=prefix,
                                      suffix=suffix,
                                      name_folder=name_folder)
        addr_movie = opj(self.dir_mda_temp, name_movie)
        out = cv2.VideoWriter(addr_movie,
                              cv2.VideoWriter_fourcc(*'DIVX'),
                              15, (self.size, self.size))
        for img in self.list_imgs_vid:
            out.write(img)
        out.release()

    def make_vid_tif(self, name_movie=''):
        '''
        Make video with tif format
        '''
        self.make_list_imgs_for_composite_video()   # list for composite video
        addr_movie = opj(self.dir_mda_temp, name_movie)
        img_final = np.empty((len(self.list_imgs_vid), 512, 512, 3))
        for i, img in enumerate(self.list_imgs_vid):
            img_final[i, :, :] = img
        io.imsave(addr_movie, img_final)

    def create_video(self, prefix='', suffix='',
                     name_folder='imgs_for_videos', name_movie='movie.avi',
                     composite_tif=False, debug=[]):
        '''
        Create a video for each position
        '''
        if 1 in debug:
            print(f'#### Creating video with prefix {prefix}')
            print(f'#### Creating video with suffix {suffix}')
            print(f'#### Creating video with name {name_movie}')
        if composite_tif:
            self.make_vid_tif(name_movie=name_movie)
        else:
            self.make_vid_avi(prefix=prefix,
                              suffix=suffix,
                              name_folder=name_folder,
                              name_movie=name_movie)
