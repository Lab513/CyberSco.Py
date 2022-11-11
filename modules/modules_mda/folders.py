import oyaml as yaml
import shutil as sh
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename


class FOLDERS():
    '''
    MDA experiment folders
    '''
    def __init__(self, debug=[0]):
        '''
        Folders for the MDA
        '''
        pass

    def folder_exp(self):           # folder experiment
        '''
        Handle the temporary mda folder
        '''
        self.dir_mda_temp = opj(os.getcwd(), 'mda_temp')      # mda folder
        with open('interface/settings/dash_monitor_addr.yaml') as f_r:
            self.dash_monitor_addr = yaml.load(f_r, Loader=yaml.FullLoader)
        self.dir_mda_temp_dash = f'{self.dash_monitor_addr}/mda_temp_{self.user.name}'
        self.dir_test = opj(os.getcwd(), 'test')          # test folder
        # folder for init params of the predefined mda
        mda_init = opj(self.dir_mda_temp, 'mda_init')
        # folder for producing video
        imgs_videos = opj(self.dir_mda_temp, 'imgs_for_videos')
        # folder for producing BF-RFP video
        imgs_BF_fluo_videos = opj(self.dir_mda_temp, 'imgs_for_BF_RFP_videos')
        # folder for producing GFP video
        imgs_GFP_videos = opj(self.dir_mda_temp, 'imgs_for_GFP_videos')
        # folder for the monitorings
        monitorings = opj(self.dir_mda_temp, 'monitorings')
        # folder for BF
        BF = opj(self.dir_mda_temp, 'monitorings', 'BF')
        # folder for predictions
        pred = opj(self.dir_mda_temp, 'monitorings', 'pred')
        # folder for contours
        cntrs = opj(self.dir_mda_temp, 'monitorings', 'cntrs')
        # folder for nb_cells
        nb_cells = opj(self.dir_mda_temp, 'monitorings', 'nb_cells')
        # folder for the tracking
        tracking = opj(self.dir_mda_temp, 'monitorings', 'tracking')
        # folder for superp_cntrs
        superp_cntrs = opj(self.dir_mda_temp, 'monitorings', 'superp_cntrs')
        # folder for events
        events = opj(self.dir_mda_temp, 'monitorings', 'events')
        # folder for autofocus
        AF = opj(self.dir_mda_temp, 'monitorings', 'AF')
        # folder for autofocus ML images
        AF_ML = opj(self.dir_mda_temp, 'monitorings', 'AF', 'ML')
        # folder for autofocus Laplacian images
        AF_Lap = opj(self.dir_mda_temp, 'monitorings', 'AF', 'Lap')
        # folder for current experiment
        experim = opj(self.dir_mda_temp, 'monitorings', 'experim')
        # folder for autofocus with ML method
        imgs_for_AF_ML = opj(self.dir_mda_temp, 'monitorings',
                             'AF', 'imgs_for_AF_ML')
        # folder for autofocus with ML method
        imgs_for_AF_ML_direct_training = opj(self.dir_mda_temp,
                                             'monitorings', 'AF',
                                             'imgs_for_AF_ML_direct_training')
        movie = opj(self.dir_test, 'movie')
        try:
            #sys.stdout.close()
            print(f'trying to remove {self.dir_mda_temp} ')
            sh.rmtree(self.dir_mda_temp)
            print('removed mda_temp')
        except:
            print('no mda folder')
        try:
            print(f'trying to remove {self.dir_mda_temp_dash} ')
            sh.rmtree(self.dir_mda_temp_dash)
            print(f'removed {self.dir_mda_temp_dash}')
        except:
            print(f'probably no {self.dir_mda_temp_dash} folder')
        try:
            sh.rmtree(self.dir_test)
        except:
            print('no test folder')
        os.makedirs(self.dir_mda_temp)               # mda folder
        try:
            os.makedirs(self.dir_mda_temp_dash)          # mda folder for the Dashboard
        except:
            print('Cannot create the folder for the Dashboard')
        os.makedirs(imgs_videos)
        os.makedirs(mda_init)
        os.makedirs(imgs_BF_fluo_videos)
        os.makedirs(imgs_GFP_videos)
        os.makedirs(monitorings)
        os.makedirs(pred)
        os.makedirs(BF)
        os.makedirs(cntrs)
        os.makedirs(nb_cells)
        os.makedirs(tracking)
        os.makedirs(superp_cntrs)
        os.makedirs(events)
        os.makedirs(AF)
        os.makedirs(AF_ML)
        os.makedirs(AF_Lap)
        os.makedirs(experim)
        os.makedirs(imgs_for_AF_ML)
        os.makedirs(imgs_for_AF_ML_direct_training)
        os.makedirs(movie)
        self.init_count_rep()
        self.init_pic_time()
        self.init_info_sensors()
