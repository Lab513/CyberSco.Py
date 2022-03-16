#!/usr/bin/env python
# encoding: utf-8

import glob
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename


class MAIL_ATTACH(object):
    '''

    '''
    def __init__(self):
        pass

    def attach_BF_image(self, pos, rep):
        '''
        Attach last image of the position
        '''
        addr_BF = opj(self.dir_mda_temp, f'frame{pos.num}_t{rep}.tiff')
        if os.path.exists(addr_BF):
            self.attach += [addr_BF]

    def attach_BF_video(self, pos):
        '''
        Attach last video of the position
        '''
        addr_vid_BF = opj(self.dir_mda_temp, f'movie_pos{pos.num}.avi')
        if os.path.exists(addr_vid_BF):
            self.attach += [addr_vid_BF]

    def attach_pos_z(self, pos):
        '''
        Attach last graph for z position
        '''
        addr_posz = opj(self.dir_mda_temp, 'monitorings', 'AF',
                        f'list_focusML_z_pos{pos.num}.html')
        if os.path.exists(addr_posz):
            self.attach += [addr_posz]

    def attach_ML_focus_curve(self, pos, rep):
        '''
        Attach last curve for AF with ML
        '''
        addr_ML_curve = opj(self.dir_mda_temp, 'monitorings', 'AF',
                            f'evol_surf_pred{pos.num}_t{rep}.png')
        if os.path.exists(addr_ML_curve):
            self.attach += [addr_ML_curve]

    def attach_tracking_video(self, pos):
        '''
        Attach tracking video
        '''
        tracking_video = opj(self.dir_mda_temp, 'monitorings',
                             f'movie_tracking{pos.num}.avi')
        if os.path.exists(tracking_video):
            self.attach += [tracking_video]

    def attach_superp_video(self, pos):
        '''
        Attach superp video
        '''
        superp_video = opj(self.dir_mda_temp, 'monitorings',
                           f'movie_superp{pos.num}.avi')
        if os.path.exists(superp_video):
            self.attach += [superp_video]

    def attach_AF_ML_video(self, pos):
        '''
        Attach AF ML video
        '''
        af_ml_video = opj(self.dir_mda_temp, 'monitorings', 'AF',
                          f'movie_AF_ML{pos.num}.avi')
        if os.path.exists(af_ml_video):
            self.attach += [af_ml_video]

    def attach_AF_Lap_video(self, pos):
        '''
        Attach AF Lap video
        '''
        af_lap_video = opj(self.dir_mda_temp, 'monitorings', 'AF',
                           f'movie_AF_Lap{pos.num}.avi')
        if os.path.exists(af_lap_video):
            self.attach += [af_lap_video]

    def attach_AF_list_posz(self, pos):
        '''
        Attach the Bokeh file por z pos
        '''
        posz_list_html = f'list_focusML_z_pos{pos.num}.html'
        af_list_posz_html = opj(self.dir_mda_temp, 'monitorings',
                                'AF', posz_list_html)
        if os.path.exists(af_list_posz_html):
            self.attach += [af_list_posz_html]

    def attach_bf_rfp_video(self, pos):
        '''
        Attach bf rfp video
        '''
        bf_rfp_video = opj(self.dir_mda_temp,
                           f'movie_pos{pos.num}_BF_fluo.avi')
        if os.path.exists(bf_rfp_video):
            self.attach += [bf_rfp_video]

    def attach_gfp_video(self, pos):
        '''
        Attach gfp video
        '''
        gfp_video = opj(self.dir_mda_temp, f'movie_pos{pos.num}_GFP.avi')
        if os.path.exists(gfp_video):
            self.attach += [gfp_video]

    def attach_bf_rfp_buds_video(self, pos):
        '''
        Attach bf rfp video
        '''
        bf_rfp_buds_video = opj(self.dir_mda_temp,
                                f'movie_pos{pos.num}_BF_fluo_buds.avi')
        if os.path.exists(bf_rfp_buds_video):
            self.attach += [bf_rfp_buds_video]

    def attach_experim_infos(self):
        '''
        Attach infos about the experiment
        '''
        addr_experim_infos = opj(self.dir_mda_temp, f'experiment_infos.yaml')
        if os.path.exists(addr_experim_infos):
            self.attach += [addr_experim_infos]

    def attach_log_file(self):
        '''
        Attach the log_file
        '''
        log_file = opj(self.dir_mda_temp, f'log.dat')
        if os.path.exists(log_file):
            self.attach += [log_file]

    def attach_events_images(self, pos):
        '''
        Attach images of the events with a mark on the event
        '''
        addr_events = opj(self.dir_mda_temp, 'monitorings', 'events')
        list_events = glob.glob(opj(addr_events,
                                f'triggering_event{pos.num}*.tiff'))
        for ev_img in list_events:
            self.attach += [ev_img]
