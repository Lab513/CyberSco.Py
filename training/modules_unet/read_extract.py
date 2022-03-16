'''
Read the films and extract the pictures
'''
import os
opb = os.path.basename
opd = os.path.dirname
opj = os.path.join
from pathlib import Path
import json
import shutil as sh
##
from PIL import Image
##
import numpy as np
##
from matplotlib import pyplot as plt
import cv2

class READ_EXTRACT():
    '''
    Read video and extract images
    '''
    def path_proc_temp_with_root(self,root):
        '''
        path for temporary processings
        '''
        p = root / self.dir_all_procs / ('proc_temp')        #
        return p

    def path_proc_with_root(self,root):
        '''
        path for processings
        '''
        p = root / self.dir_all_procs / ('proc_' + self.date)    # dir_all_procs by default is processings
        return p

    def server_paths(self):
        '''
        Server paths
        '''
        path_static = Path('image_analysis') / 'static'                  # static address for server usage
        self.path_procs_static = path_static / 'processings'             # server processings folder
        self.folder_curr_pic = path_static / 'curr_pic'                  # current pic for server

    def processings_path(self):
        '''
        Path where are saved the results
        '''
        if self.args.save_in:
            if 'processings' and 'proc_' in str(self.args.save_in) :
                self.dir_result = self.args.save_in
            else:
                root = Path(self.args.save_in)
                self.dir_result = self.path_proc_with_root(root)
                self.dir_result_temp = self.path_proc_temp_with_root(root)
        else:
            self.args.save_in = Path('.')
            self.dir_result = self.path_proc_with_root(self.args.save_in)
            self.dir_result_temp = self.path_proc_temp_with_root(self.args.save_in)

    def prepare_paths_and_names(self):
        '''
        Prepare the addresses and variables for processing
        '''
        self.output_folder = Path('test') / 'movie' #
        self.output_folder_gray = Path('test') / 'movie_gray'
        self.output_folder_events = Path('test') / 'events'
        self.dir_all_procs =  Path('.') / 'processings'                  # path for all the processings
        self.film_addr = self.args.film                                  # address of the film
        dirname = os.path.basename(os.path.dirname(self.args.film))
        filmname = os.path.basename(self.film_addr)[:-4]                 # file name
        self.name_film = dirname + '_' + filmname
        ##
        self.model = self.args.model                                     # model
        self.model_events = self.args.model_events                       # model for events like buds detection etc..
        self.server_paths()                                              # paths for the server part
        self.processings_path()                                          # paths for the results

    def remove_folders(self):
        '''
        Remove the temporary folders:
            predicition/movie
            test/movie
            test/movie_fluo
            image_analysis/static/processings
        '''
        lfolder = [ Path('predictions')/'movie',
                    Path('test') / 'movie',
                    Path('test') / 'movie_fluo',
                    Path('test') / 'movie_gray',
                    Path('test') / 'events',
                    Path('image_analysis')/'static'/'processings',
                    Path('processings') / 'proc_temp' ]
        for fold in lfolder:
            try:
                sh.rmtree(fold)
                print('removed ', fold)
            except:
                pass

    def test_exists_mkdir(self, path):
        '''
        Check if the dir exists and make it if not
        '''
        if not os.path.exists(str(path)):
            os.makedirs(str(path))
            print("made path ", path)

    def show_created_folders(self):
        '''
        Folders for processing
        '''
        print("############ prepare folders !! ############## ")
        print(self.output_folder)
        print(self.dir_all_procs)
        print(self.dir_result)
        print(self.dir_result_temp)
        print(self.path_procs_static)

    def prepare_folders(self):
        '''
        Make the output folders
        '''
        self.show_created_folders()
        self.test_exists_mkdir(self.output_folder)            # test/movie
        self.test_exists_mkdir(self.dir_all_procs)            # processings
        self.test_exists_mkdir(self.dir_result)               # processings/proc_date
        self.test_exists_mkdir(self.dir_result_temp)          # processings/proc_temp
        self.test_exists_mkdir(self.path_procs_static)        # image_analysis/static/processings
        self.test_exists_mkdir(self.folder_curr_pic)          # image_analysis/static/curr_dir (control processing in real time)
        self.test_exists_mkdir(Path('models'))                # folder for the models
        self.test_exists_mkdir(Path('masks'))                 # folder for the masks
        if self.args.gray_img:
            self.test_exists_mkdir(self.output_folder_gray)
        self.test_exists_mkdir(self.output_folder_events)

    def save_gray(self, addr_img):
        '''
        Save in grayscale
        '''
        if self.args.gray_img:
            img = Image.open(addr_img).convert('L')
            img.save( str(self.output_folder_gray / opb(addr_img)) )

    def extract_BF(self):
        '''
        Extract the images from the video
        and save them in self.output_folder
        as self.size x self.size pictures with extension self.ext..
        '''
        ext = os.path.splitext(self.film_addr)[1]
        print('#### extension is {0} !!! '.format(ext))
        if ext in ['.mp4','.avi']:
            self.read_extract_avi()
        elif ext == '.tif':
            self.read_extract_tif()

    def read_extract_avi(self):
        '''
        Read avi video and extract images
        '''
        vidcap = cv2.VideoCapture(self.film_addr)
        success, img = vidcap.read()
        count = 0
        while success:
            addr_img = str(self.output_folder / f"frame{count}.{self.ext}")
            print(addr_img)
            cv2.imwrite( addr_img, img )     # save frame in self.output_folder
            self.save_gray(addr_img)         # triggered if self.args.gray_img True
            success, img = vidcap.read()
            count += 1

    def resize_img(self, img, debug=0):
        '''
        Resize the images to the size : self.size
        '''
        res = cv2.resize(img, dsize=(self.size, self.size), interpolation=cv2.INTER_CUBIC) # dsize=(512, 512)
        if debug > 0:
            print("res.shape ", res.shape)
        ##  Remove axes, remove axis
        dpi_val = 100
        fig = plt.figure(figsize=(self.size/dpi_val, self.size/dpi_val), dpi=dpi_val)
        ax = plt.Axes(fig, [0., 0., 1., 1.])
        ax.set_axis_off()
        fig.add_axes(ax)
        ax.imshow(res, aspect='equal', cmap='gray')

    def read_extract_tif(self):
        '''
        Read tif videos and extract images
        '''
        print("The selected stack is a .tif")
        dataset = Image.open(self.film_addr)
        h,w = np.shape(dataset)
        for i in range(dataset.n_frames):
            addr_img = str(self.output_folder / f"frame{i}.{self.ext}")
            print(addr_img)
            dataset.seek(i)
            img = np.array(dataset).astype(np.double)
            #print("img.shape ", img.shape)
            self.resize_img(img)
            plt.savefig( addr_img, dpi=100 )       # save frame in self.output_folder
            self.save_gray(addr_img)               # triggered if self.args.gray_img True

    def extract_images(self):
        '''
        Extract the images from the videos
        '''
        self.extract_BF()            # extract BF images
        if self.args.rfp:
            self.extract_RFP()       # extract RFP images

    def extract_RFP(self):
        '''
        Extract the images from RFP file to test/movie_fluo
        '''
        self.output_folder = Path('test') / 'movie_fluo' #
        self.film_addr = self.args.rfp
        print(f"##### self.film_addr is {self.film_addr}")
        self.prepare_folders()
        self.extract_BF()
        self.output_folder = Path('test') / 'movie'    # redefine as before self.output_folder
        self.film_addr = self.args.film
