import os, sys
op = os.path
opb, opd, opj = op.basename, op.dirname, op.join
import pickle as pkl
from pathlib import Path
#from util_misc import copy_dir
from time import time, sleep
from flask_socketio import emit
from analyse_results import ANALYSE_RESULTS as AR

from util_server import *
from util_misc import *
platf  = find_platform()
server = chose_server(platf)

class SAVE_RESULTS():
    '''
    Save the results of the processings in the right places
    '''

    def save_cntr_pkl(self, cntrs, name):
        '''
        Save the contours for further analysis
        '''
        with open( name ,'wb' ) as f:
            pkl.dump(cntrs,f)

    def save_all_contours(self):
        '''
        Save both the contours from post prediction and prediction
        '''

        plk_cntrs_dir = self.generic_result_name_dir('pkl_cntrs')
        plk_cntrs_pred_dir = self.generic_result_name_dir('pkl_cntrs_pred')
        self.plk_cntrs_dir_temp = self.generic_result_name_dir_temp('pkl_cntrs')
        self.plk_cntrs_pred_dir_temp = self.generic_result_name_dir_temp('pkl_cntrs_pred')
        self.save_cntr_pkl( self.contours, f'{plk_cntrs_dir}.pkl' )
        self.save_cntr_pkl( self.contours_pred, f'{plk_cntrs_pred_dir}.pkl' )         # pickle the contours of predictions
        self.save_cntr_pkl( self.contours, f'{self.plk_cntrs_dir_temp}.pkl' )
        self.save_cntr_pkl( self.contours_pred, f'{self.plk_cntrs_pred_dir_temp}.pkl' )         # pickle the contours of predictions

    def clean_curr_pic_folder(self):
        '''
        Clean the folder for following the processing
        '''

        for f in os.listdir(self.folder_curr_pic):  # remove the pics
            print("image_analysis / static / curr_pic", f)
            try:
                os.remove( str(self.folder_curr_pic / f) )
            except:
                pass

    def copy_curr_pic_in_server(self):
        '''
        Copy the current processed pic in the server
        so that the user can access from the interface
        to real time control of processing quality
        '''
        curr_frame = f'frame{self.num}.png'
        addr_pic_pred = self.dir_movie_pred / curr_frame                               # address in predictions folder
        self.addr_pic_server = self.folder_curr_pic / curr_frame                       # address in server
        self.addr_relative_pic_server = Path('static') / 'curr_pic' / curr_frame       # relative address in the server
        self.clean_curr_pic_folder()
        sh.copy(addr_pic_pred, self.addr_pic_server )

    def emit_addr_curr_pic(self):
        '''
        path for the pic lastly processed saved in the server
        '''
        # self.copy_curr_pic_in_server()
        # sleep(self.sleep_time)
        # emit( 'res_dir', { 'mess': str(self.addr_relative_pic_server) } )         # emit address of the folder with images processed..
        # server.sleep(self.ts_sleep)

        try:
            self.copy_curr_pic_in_server()
            sleep(self.sleep_time)
            emit( 'res_dir', { 'mess': str( self.addr_relative_pic_server ) } )         # emit address of the folder with images processed..
            server.sleep(self.ts_sleep)
        except:
            print('cannot save pic in the server')

    def emit_proc_result_address(self):
        '''
        Emit the address of the processed images
        '''

        # sleep(self.sleep_time)
        # res_proc_static_addr = Path('static/processings') / opb(self.dir_movie_pred)
        # emit( 'server_res_dir', { 'mess': str(res_proc_static_addr) } )         # emit address of the folder with images processed..
        # server.sleep(self.ts_sleep)

        try:
            sleep(self.sleep_time)
            res_proc_static_addr = Path('static') / 'processings' / opb(self.dir_movie_pred)
            emit( 'server_res_dir', { 'mess': str(res_proc_static_addr) } )         # emit address of the folder with images processed..
            server.sleep(self.ts_sleep)
        except:
            print('cannot emit address addr of resulting procs')

    def copy_in_dir(self, dir):
        '''
        Copy proc and orig in folder dir..
        '''
        [ copy_dir(d, dir) for d in [ self.proc_folder, self.orig_folder ] ]

    def copy_in_dir_result(self):
        '''
        Copy the results in a folder with date
        '''
        self.copy_in_dir(self.dir_result)

    def copy_in_dir_result_temp(self):
        '''
        Copy the results in a temporary folder
        '''
        self.copy_in_dir(self.dir_result_temp)

    def copy_folders(self):
        '''
        After each processing, copy the folder in self.dir_result and self.dir_result_temp
        '''
        self.proc_folder = self.dir_movie_pred.resolve().parent       # folder above folder results
        print("### self.proc_folder is ", self.proc_folder)
        self.orig_folder = self.output_folder.resolve().parent        # folder above folder with original images
        self.copy_in_dir_result()                                     # processings/proc_ + date
        self.copy_in_dir_result_temp()                                # processings/proc_temp
        copy_dir(self.proc_folder, self.path_procs_static)            # static/processings (server)
        self.emit_proc_result_address()                               # emit the address of the folder with processed images
        self.analyse_and_jsonify()

    def analyse_and_jsonify(self):
        '''
        '''
        try:
            self.ar = AR(name_result= self.plk_cntrs_dir_temp + '.pkl')
            self.ar.make_json( opj(opd(self.plk_cntrs_dir_temp),'analysis_infos' + '.json') ) # save the json file in processings/proc_temp
        except:
            print('Probably error with self.plk_cntrs_dir_temp')

    def save_proc_results(self):
        '''
        After the processing is achieved, save the results in 'proc_date' folder..
        '''
        if self.args.track or self.args.show_pred :
            self.save_all_contours()
            self.copy_folders()
