

class MAKE_VIDEOS_POSITION():
    '''
    Create the videos from png pictures obtain
    for the experiments, the monitorings etc..
    '''
    def __init__(self):
        '''

        '''

    def make_video_positions(self, rep, step=5, debug=[]):
        '''
        Make a video for each position
        '''
        if rep % step == 0:
            if 1 in debug:
                print(f'**** At rep {rep} make the videos ****')
            for pos in self.list_pos:
                # BF movie
                pos.create_video(name_movie=f'movie_pos{pos.num}.avi')
                # try:
                # superposition rfp BF
                pos.create_video(prefix='superp_bf_fluo_frame',
                                 name_folder='imgs_for_BF_RFP_videos',
                                 name_movie=f'movie_pos{pos.num}_BF_fluo.avi')
                # GFP
                pos.create_video(prefix='frame',
                                 suffix='_gfp',
                                 name_folder='imgs_for_GFP_videos',
                                 name_movie=f'movie_pos{pos.num}_GFP.avi')
                # superposition rfp BF and buds
                pos.create_video(prefix='superp_with_buds_frame',
                                 name_folder='imgs_for_BF_RFP_videos',
                                 name_movie=f'movie_pos{pos.num}_'
                                            f'BF_fluo_buds.avi')
                # buds via segm area video
                pos.create_video(prefix='buds_frame',
                                 name_folder='monitorings/tracking',
                                 name_movie=f'monitorings/movie'
                                            f'_tracking_buds{pos.num}.avi')
                # tracking video
                pos.create_video(prefix='track_frame',
                                 name_folder='monitorings/tracking',
                                 name_movie=f'monitorings/'
                                            f'movie_tracking{pos.num}.avi')
                # segmentation superposition video
                pos.create_video(prefix='pred_frame',
                                 name_folder='monitorings/superp_cntrs',
                                 name_movie=f'monitorings/movie'
                                            f'_superp{pos.num}.avi')
                # AF ML
                pos.create_video(prefix='evol_surf_pred',
                                 name_folder='monitorings/AF/ML',
                                 name_movie=f'monitorings/AF/'
                                            f'movie_AF_ML{pos.num}.avi')
                # AF Laplacian
                pos.create_video(prefix='evol_lap_var',
                                 name_folder='monitorings/AF/Lap',
                                 name_movie=f'monitorings/AF/'
                                            f'movie_AF_Lap{pos.num}.avi')
                # Composite video, BF, RFP, GFP
                try:
                    pos.create_video(prefix='',
                                     name_folder='',
                                     name_movie=f'composite_bf'
                                                f'_rfp_gfp_pos{pos.num}.avi')
                except:
                    print('#### Cannot create composite video !!!')
