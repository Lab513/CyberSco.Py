import os, glob
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join
from time import sleep, time
from colorama import Fore, Style
from pathlib import Path
import shutil as sh
import yaml
from matplotlib import pyplot as plt
try:
    from devices.modules_Olymp.focus_segm_plots.AF_ML_plots import FOCUS_SEGM_PLOT as FSP
    from devices.modules_Olymp.focus_segm_plots.find_optim_focus import FIND_OPTIM_FOCUS as FOF
except:
    from modules.devices.modules_Olymp.focus_segm_plots.AF_ML_plots import FOCUS_SEGM_PLOT as FSP
    from modules.devices.modules_Olymp.focus_segm_plots.find_optim_focus import FIND_OPTIM_FOCUS as FOF
import numpy as np
from scipy.optimize import curve_fit
import cv2

# https://neurodiscovery.harvard.edu/files/hndc/files/ix81_zdc.pdf page 3
# https://documents.epfl.ch/users/r/ro/ross/www/fjr0021-ix81_command.html

class FOCUS_SEGM(FSP, FOF):
    '''
    Focus with segmentation
    The optimal focus is the z value corresponding
    to the maximal segmentation area.
    The steepest positive slope is used for finding the optimum.
    '''
    # nb_af_steps=10, step_width=1 # 18,2 for sucrose # 30,1 test AF
    def __init__(self, nb_af_steps=11, step_width=0.25):
        '''
        nb_af_steps : nb of steps
        step_width : z step width in µm
        '''
        lcls = [FSP, FOF]
        [cl.__init__(self) for cl in lcls]
        self.nbbytes = 11              # nb of bytes for serial
        # list of optimal indices for ML method
        self.list_focusML_index = []
        # list of optimal z with ML method
        self.list_focusML_zpos = []
        # list of optimal indices for Laplacian method
        self.list_focusLap_index = []
        # number of steps for searching the focus, 5--> 7s, 8-->12s
        self.focus_nbsteps = nb_af_steps
        # plus and minus delta in hundredth of µm
        self.delta_focus = nb_af_steps*step_width*50
        # step for searching the focus with ML
        self.step_focus = int(2*self.delta_focus / self.focus_nbsteps)
        self.mean_surf = True
        # frequence for saving af images for training
        self.freq_af_train = 1
        # list of the durations for AFML correction
        self.list_AFML_duration = []
        self.prepare_addr_for_AF_ML()
        self.afml_max_area = 300
        self.thresh = 127

    def prepare_addr_for_AF_ML(self):
        '''
        '''
        self.addr_direct_AF_ML = opj('mda_temp', 'monitorings',
                                     'AF', 'imgs_for_AF_ML_direct_training')

    def take_pic_posz(self, i, val, suffix='', addr=None,
                                    move_type=None, bpp=8, show=False):
        '''
        take a BF picture at posz =  val
        '''
        self.set_wheel_filter(1)              # set wheel filter for BF
        if i == 1664 or i == 0 : sleep(0.5)
        if not self.shut:
            self.set_shutter(shut='on')       # shutter
        sleep(1)
        self.go_zpos(val, move_type=move_type)        # 797300
        answ = self.receive(13)
        print(f'answ 0 {answ}')
        suffix = '_' + suffix
        if addr:
            self.addr_img_optimz = addr
        else:
            self.addr_img_optimz = opj('mda_temp', 'monitorings',
                'AF', 'imgs_for_AF_ML', f'bf_for_optimz{i}{suffix}.tiff')
        self.cam.take_pic(self.addr_img_optimz, bpp=bpp,
                          exp_time=100, allow_contrast=True)
        # self.cam.adapt(bpp)                # adapt the pixel range
        if show:
            plt.figure()
            plt.title(f'cam frame {i}')
            plt.imshow(self.cam.frame, cmap='gray')
            plt.show()
        return self.cam.frame

    def debug_make_pred(self, pred_surf, pred):
        '''
        '''
        print(f'pred_surf {pred_surf}')
        addr_pred = f'pred_uu{i}.png'
        cv2.imwrite(addr_pred, pred)

    def make_pred(self, i, show=False,
                save=True, surf_tot=True, debug=[]):  # thresh in x60 is 253
        '''
        make the prediction and return surface
        '''
        img = cv2.imread(self.addr_img_optimz)
        if 0 in debug:
            print(f'Using self.addr_img_optimz'\
                f' {self.addr_img_optimz} for make_pred !!!')
        h, w, nchan = img.shape
        mask = np.zeros((h, w), np.uint8 )
        # format array for prediction
        arr = np.array([img], dtype=np.float32)/255
        pred = self.mod_afml.predict(arr)[0]*255
        ##
        nbcntrs = 0
        pred_surf = 0
        # threshold on the prediction
        ret, thr = cv2.threshold(pred, self.thresh, 255, 0)
        thr = thr.astype(np.uint8)
        # find contours
        cntrs, _ = cv2.findContours(thr, cv2.RETR_TREE,
                                    cv2.CHAIN_APPROX_SIMPLE)[-2:]

        for c in cntrs:
            carea = cv2.contourArea(c)
            # removing large shapes
            if carea < self.afml_max_area:
                pred_surf += carea
                nbcntrs += 1
                # fill contour
                cv2.drawContours(mask, [c], -1, (255, 255, 255), -1)
        if nbcntrs == 0 or surf_tot : nbcntrs = 1
        #len(np.where(pred > self.thresh)[0]) / nbcntrs
        pred_surf_mean = round(pred_surf / nbcntrs, 1)
        pred_surf_mask_mean = round(len(
                np.where(mask > self.thresh)[0]) / nbcntrs, 1)
        if 1 in debug: self.debug_make_pred(pred_surf_mean, pred)
        if 2 in debug:
            print(f'pred_surf_mean is {pred_surf_mean} ')
            print(f'pred_surf_mask_mean is {pred_surf_mask_mean} ')
        if show:
            plt.figure()
            plt.imshow(pred, cmap='gray')
        if save:
            plt.figure()
            plt.imshow(pred, cmap='gray')
            # address for pred
            addr_pred_af = self.addr_img_optimz[:-5] + 'pred.png'
            if 3 in debug: print(f'save pred at address {addr_pred_af} ')
            plt.axis('off')
            plt.savefig(addr_pred_af, bbox_inches='tight', pad_inches=0)
            addr_cntrs_filtered_af = self.addr_img_optimz[:-5] +\
                                                    'cntrs_filtered.png'
            cv2.imwrite(addr_cntrs_filtered_af , mask)

        return pred_surf_mean

    def make_surf_pred_list(self, ref, debug=[1]):
        '''
        List of the prediction surfaces
        '''
        # list of the surfaces
        l_surf = []
        # list of the value of the variance of the Laplacian
        l_lap = []
        for i in range(self.focus_nbsteps):
            print(f'i is {i} ')
            posz = ref + i*self.step_focus
            print(f'posz is {posz} ')
            # take a picture at z pos ref + i*step
            self.take_pic_posz(i, posz, move_type='d')
            # variance of the Laplacian
            lap = cv2.Laplacian(self.cam.frame.astype('uint8'), 3).var()
            l_lap += [lap]
            # add surface of pred to l_surf
            l_surf += [self.make_pred(i)]
        # register the curve
        if self.rep == 0:
            self.ref_l_surf = l_surf
            if 1 in debug:
                print(f'### self.ref_l_surf is {self.ref_l_surf}')

        return l_surf, l_lap

    def messages_refocus_segm(self,t0,t1,ind_optim,pos_focus):
        '''
        time for focusing with ML, index max found and position chosen for focus
        '''
        print(f'time elapsed for the focus ML is {round((t1-t0) , 1)} s')
        print(Fore.YELLOW + '------------------')
        print(f'ind_optim is {ind_optim}')
        print('------------------')
        print(f'pos_focus ML is {pos_focus}')
        print(Style.RESET_ALL)

    def find_steepest_left(self, l_surf):
        '''
        Find the optimal focus using the steepest
            position in l_surf on the left edge
        '''
        diff = np.diff(np.array(l_surf))        # derivative of l_surf
        cnd1 = diff > 0                         # positive derivative
        cnd2 = diff > diff.max() - 0.1          # max derivative
        # index respecting the conditions cnd1 and cnd2
        index_steepest = np.where(cnd1 & cnd2)[0][0] + 1
        self.follow_index_optim(index_steepest)
        # if surf associated to index_steepest too low, increment of one unit
        if abs(max(l_surf) - l_surf[index_steepest]) / max(l_surf) > 0.25:
            index_steepest += 1
        return index_steepest

    def find_steepest_right(self, l_surf):
        '''
        Find the optimal focus using the steepest
                position in l_surf on the right edge
        '''
        diff = np.diff(np.array(l_surf))              # derivative of l_surf
        cnd1 = diff < 0                               # positive derivative
        sec_max = sorted(np.abs(diff))[-2]
        cnd2 = np.abs(diff) >= sec_max                # max derivative
        # index respecting the conditions cnd1 and cnd2
        index_steepest = np.where(cnd1 & cnd2)[0][0]
        # if surf associated to index_steepest too low, increment of one unit
        if abs(max(l_surf) - l_surf[index_steepest]) / max(l_surf) > 0.25:
            index_steepest += 1
        return index_steepest

    def steep_max_left_calc(self, l_surf, debug=[1]):
        '''
        Find steepest on the left and choose with max
        '''
        ind_max = l_surf.index(max(l_surf))     # take the maximum
        try:
            # index for the steepest slope
            ind_steepest_left = self.find_steepest_left(l_surf)
        except:
            print('Cannot find steepest')
            ind_steepest_left = ind_max
        relat_diff = abs(l_surf[ind_max] -
                    l_surf[ind_steepest_left])/l_surf[ind_max]
        if relat_diff < 0.1:
            optim_ind = ind_steepest_left
        else:
            optim_ind = ind_max

        return optim_ind

    def steep_max_right_calc(self, l_surf, debug=[1,2]):
        '''
        Find steepest on the right and choose with max
        '''
        ind_max = l_surf.index(max(l_surf))     # take the maximum
        try:
            # index for the steepest slope
            ind_steepest_right = self.find_steepest_right(l_surf)
        except:
            print('Cannot find steepest')
            ind_steepest_right = ind_max
        if 1 in debug:
            print(f'ind_max = {ind_max}, '\
              'ind_steepest_right = {ind_steepest_right}')
        relat_diff = abs(l_surf[ind_max] -
                l_surf[ind_steepest_right])/l_surf[ind_max]
        if 2 in debug: print(f'relat_diff = {relat_diff}')
        if relat_diff < 0.1:
            optim_ind = ind_steepest_right
        else:
            optim_ind = ind_max

        return optim_ind

    def find_optim(self, l_surf, debug=[1]):
        '''
        Find the optimum for the the afml full
         sweep method once the curve is done.
        '''

        if self.afml_optim  == 'steep_max_left':             # max or left edge
            ind_optim = self.steep_max_left_calc(l_surf)
        elif self.afml_optim  == 'steep_max_right':         # max or right edge
            ind_optim = self.steep_max_right_calc(l_surf)
        elif self.afml_optim  == 'steep_right':                # right edge
            ind_optim = self.find_steepest_right(l_surf)
        elif self.afml_optim  == 'max':                        # max
            ind_optim = l_surf.index(max(l_surf))

        return ind_optim

    def make_AF_ML_direct_training(self, ref, rep, ind_optim):
        '''
        Make file for labels for direct AF ML
        '''
        if ref%self.freq_af_train == 0 :
            pos_focus = ref + ind_optim*self.step_focus
            self.fill_folder_for_AF_ML_direct_training(rep, ref, pos_focus)

    def write_AF_img_name_dist(self, label_file, ref, i, pos_focus, addr_targ):
        '''
        Write the filename of the image with the distance to the z optimal
        '''
        curr_posz = ref + i*self.step_focus
        dist = curr_posz - pos_focus
        name_img = opb(addr_targ)
        label_file.write(f'{name_img} {dist}\n')

    def copy_bf_zstack(self, ll, ref, rep, label_file, pos_focus, debug=[]):
        '''
        '''
        for i,addr_img in enumerate(ll):
            new_name = opb(addr_img).split('.tiff')[0] +\
                                f'pos{self.num}_t{rep}.tiff'
            # target adddress
            addr_targ = opj(self.addr_direct_AF_ML, new_name)
            if 1 in debug:
                print(f'addr_img is {addr_img}')
                print(f'addr_targ is {addr_targ}')
            sh.copy(addr_img, addr_targ)
            ###
            self.write_AF_img_name_dist(label_file, ref,
                                    i, pos_focus, addr_targ)

    def copy_zstack_pred(self, lpred, ref, rep, pos_focus, debug=[]):
        '''
        '''
        for i,addr_img in enumerate(lpred):
            new_name = opb(addr_img).split('.png')[0] + \
                            f'pos{self.num}_t{rep}.png'
            # target adddress
            addr_targ = opj(self.addr_direct_AF_ML, new_name)
            if 1 in debug:
                print(f'addr_img is {addr_img}')
                print(f'addr_targ is {addr_targ}')
            sh.copy(addr_img, addr_targ)

    def fill_folder_for_AF_ML_direct_training(self, rep,
                                            ref, pos_focus, debug=[]):
        '''
        Retrieve z stacks for training
        '''
        ll = glob.glob(opj('mda_temp', 'monitorings',
                     'AF', 'imgs_for_AF_ML', '*.tiff'))
        lpred = glob.glob(opj('mda_temp', 'monitorings',
                     'AF', 'imgs_for_AF_ML', '*.png'))
        with open(self.addr_labels, 'a') as label_file:
            self.copy_bf_zstack(ll, ref, rep, label_file, pos_focus)
        self.copy_zstack_pred(lpred, ref, rep, pos_focus)

    def take_pic_at_optim(self, ind_optim, ref, rep, kind='ML'):
        '''
        Take a BF picture at optimal position in z
        '''
        if kind == 'ML':
            addr = opj('mda_temp', 'monitorings',
                    'AF', 'ML', f'optim_af_ML{rep}.png')
        else:
            addr = opj('mda_temp', 'monitorings',
                    'AF', 'Lap', f'optim_af_lap{rep}.png')
        pos_focus = ref + ind_optim*self.step_focus
        self.take_pic_posz(0, pos_focus, move_type='d', addr=addr)

    def find_surf(self, posz):
        '''
        Find segmentation surface at given position
        '''
        print(f'posz is {posz} ')
        # take a picture at posz
        self.take_pic_posz(1644, posz, move_type='d', show=False)
        surf = self.make_pred(1644)
        print(f'## surface found is {surf}')

        return surf

    def afml_refocus(self, ref_posz, ref=None, shift=-1, num='', rep='',
                    AF_train=True, reset_ref=True,
                    debug=[1,2]):
        '''
        find the focus
        ref : first position for searching
        num : position index
        reset_ref: reset the position of reference to the best position found
        AF_train : if True, produce dataset for ML training AF_ML_fast
        '''
        self.num = num                                     # position index
        self.rep = rep                                     # index of repetition in the mda
        if not ref:
            ref = ref_posz - self.delta_focus              # begin at position z=ref
            print(f'beginning position is {ref} !!!')
            print(f'ref_posz = {ref_posz} !!!')
            print(f'self.delta_focus = {self.delta_focus} !!!')
        if rep == 0:
            if 0 in debug:
                print(f'#### At beginning ref_posz = {ref_posz} ...')
        if 1 in debug:
            print(f'In afml_refocus, self.afml_optim is {self.afml_optim}..')
        if 2 in debug:
            print(f'In afml_refocus, self.step_focus is { self.step_focus }')
        if self.afml_optim == 'max':
            # find the optimum using a full sweep
            pos_focus = self.search_optim_simple_sweep(ref, rep, AF_train)
        # elif self.afml_optim == 'afml_dich':
        #     # find the optimum using dichotomy
        #     pos_focus = self.optim_with_dichotomy(rep, AF_train)
        self.go_zpos(pos_focus, 'd')      # go to the focused z position
        if reset_ref:
            ref_posz = pos_focus          # update ref_posz
            
        return ref_posz
