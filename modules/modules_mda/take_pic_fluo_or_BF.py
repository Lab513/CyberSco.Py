'''
'''
from datetime import datetime
from time import sleep
import shutil as sh
import oyaml as yaml
import os
from pathlib import Path
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join


class TAKE_PIC_FLUO_OR_BF():
    '''
    For SNAP
    '''

    def __init__(self, ol, co, emit):
        '''
        '''
        self.ol = ol
        self.co = co
        self.emit = emit
        self.settings_folder = Path('interface') / 'settings'
        self.currview = 'simple'

    def date(self):
        '''
        Return a string with day, month, year, hour, minute and seconds
        '''
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")  # -%H-%M
        return dt_string

    def snap_cases(self):
        '''
        Different possible snaps
        '''
        if self.currview == 'simple':
            addr_pic = 'interface/static/curr_pic/frame0.png'    # snap BF
        elif self.currview == 'superp':
            # snap BF + segm
            addr_pic = 'interface/static/mda_pics/pred_frame0_superp.png'
        elif self.currview == 'event':
            # snap BF + segm event
            addr_pic = 'interface/static/mda_pics/pred_ev_frame0_superp.png'
        return addr_pic

    def prepare_fluo(self, filt):
        '''
        '''
        self.ol.set_wheel_filter(filt)    # wheel filter for corresponding fluo
        self.ol.set_shutter(shut='off')      # shutter µscope off

    def prepare_RFP(self):
        '''
        Prepare wheel filter and shutter for RFP
        '''
        self.ol.set_wheel_filter(5)      # wheel filter for corresponding fluo
        self.ol.set_shutter(shut='off')                   # shutter µscope off

    def prepare_GFP(self):
        '''
        Prepare wheel filter and shutter for GFP
        '''
        self.ol.set_wheel_filter(3)       # wheel filter for corresponding fluo
        self.ol.set_shutter(shut='off')                  # shutter µscope off

    def apply_cool_SC(self, cool):
        '''
        Apply the setting channels
        '''
        for ch in ['A', 'B', 'C', 'D']:
            if cool[ch]['shut'] == 'on':
                intensity = cool[ch]['intens']
                # set the fluorescence
                set_fluo_on = f'CSS{ch}SN{str(intensity).zfill(3)}'
                print(f'set_fluo_on {set_fluo_on}')
                self.co.emit(set_fluo_on)           # trigger the fluorescence

    def return_to_BF(self):
        '''
        Return to BF parameters for shutter and wheel filter
        '''
        set_fluo_off = f'CSF'                      # set all the channels off
        print(f'set_fluo_off {set_fluo_off}')
        self.co.emit(set_fluo_off)
        self.ol.set_wheel_filter(1)                # set wheel filter for BF
        sleep(1)
        self.ol.set_shutter(shut='on')             # open the shutter for BF

    def save_snap(self, debug=[1]):
        '''
        Save the snap in interface/static/snapped
        and in Downloads
        '''
        addr_pic = self.snap_cases()
        addr_snap = 'interface/static/snapped'
        addr_targ = opj(addr_snap, f'snap_{self.date()}.png')  # snap with date
        addr_curr = opj(addr_snap, f'snap_curr.png')           # frame0.png
        print(addr_targ)
        sh.copy(addr_pic, addr_targ)
        sh.copy(addr_pic, addr_curr)
        dpath = str(Path.home() / '.jupyter' / "Downloads")
        # if not os.path.exists(dpath):
        #     os.makedirs(dpath)              # make download folder for snaps
        # sh.copy(addr_pic, dpath)
        sh.copy(addr_targ, dpath)             # save the snap in Downloads
        addr_targ
        if 1 in debug:
            print(f'save the snap in {dpath} ')

    def take_pic(self, SC_val, snap_mode=True, debug=[]):
        '''
        Snap, Take an image online
        '''
        ####
        if 1 in debug:
            print(f'SC_val is {SC_val} ')
        if 'FP' in SC_val :
            # 'rfp': {'ch':'C','filt':5}, 'gfp': {'ch':'B','filt':3}
            # current SC
            with open(self.settings_folder /
                      'settings_channels' / f'{SC_val}.yaml') as f_r:
                set_chan = yaml.load(f_r, Loader=yaml.FullLoader)
            print(f'set_chan is {set_chan}')
            if 'COOL' in set_chan.keys():
                cool = set_chan['COOL']
                print(f'cool is {cool}')
                if 'filter' not in set_chan.keys():
                    if 'RFP' in SC_val:
                        self.prepare_RFP()               # filter for RFP (5)
                    elif 'GFP' in SC_val:
                        self.prepare_GFP()               # filter for GFP (3)
                else:
                    filt = int(set_chan['filter'])
                    self.prepare_fluo(filt)
                sleep(2)
                self.apply_cool_SC(cool)
            sleep(1)
            ##
            if snap_mode:
                self.save_snap()
            self.return_to_BF()
            self.emit('snapped', 'fluo')
        else:
            if snap_mode:
                self.save_snap()
            self.emit('snapped', 'BF')

    def illuminate(self, SC_val, snap_mode=True, debug=[1]):
        '''
        Snap, Take an image in live
        '''
        ####
        if 1 in debug:
            print(f'SC_val is {SC_val} ')
        if 'FP' in SC_val:
            with open(self.settings_folder /
                      'settings_channels' / f'{SC_val}.yaml') as f_r:
                set_chan = yaml.load(f_r, Loader=yaml.FullLoader)
            print(f'In illuminate, set_chan is {set_chan}')
            if 'COOL' in set_chan.keys():
                cool = set_chan['COOL']
                print(f'cool is {cool}')
                if 'filter' not in set_chan.keys():
                    if 'RFP' in SC_val:
                        self.prepare_RFP()               # filter for RFP (5)
                    elif 'GFP' in SC_val:
                        self.prepare_GFP()               # filter for GFP (3)
                else:
                    filt = int(set_chan['filter'])
                    self.prepare_fluo(filt)
                sleep(2)
                self.apply_cool_SC(cool)
