def define_params(parser):

    parser.add_argument('-f', '--film', type=str, help='Bright Field film')         # BF
    parser.add_argument('-m', '--model', type=str, help='model trained')            # u-net model used
    parser.add_argument('--model_events', type=str, help='model for various events')            # u-net model used
    parser.add_argument('-t', '--track', type=str, help='track the cells')          # tracking arguments : nothing or list
    parser.add_argument('--nb_denoising', type=str, help='nb of denoising passes', default='0')   # nb of passes for denoising
    parser.add_argument('--nb_fits', help='nb of fits', type=str, default=99)       # nb of exponential fits
    parser.add_argument('--ratio_fit', help='', type=float, default=0.9)            # portion for fitting
    parser.add_argument('-r', '--rfp', action='store_true', help='RFP film for comparison')    # RFP
    parser.add_argument('--ellipse', action='store_true')                           # produce ellipses on the contours
    parser.add_argument('--contours', action='store_true')                          # show the contours
    parser.add_argument('--graph_nb_cells', action='store_true')                    # plot the graph of nb of cells
    parser.add_argument('--insert_graph', action='store_true')                      # plot the graph of nb of cells inside the video
    parser.add_argument('--optim_thresh', action='store_true')                      # make optim thresh test
    parser.add_argument('--video', action='store_true', default=False)              # processing with video
    parser.add_argument('--show_pred', action='store_true')                         # show the predicted masks
    parser.add_argument('--stop_at_pred', action='store_true', help='until predictions')   # stop procesing at prediction step
    parser.add_argument('--gray_img', action='store_true', help='produce gray images')   # produce gray images
    parser.add_argument('--dil_cntrs', action='store_true', help='show contours after dilation')   # show contours after dilation
    parser.add_argument('--frontiers', action='store_true', help='show frontiers betweens neighbours')
    parser.add_argument('--nuclei', action='store_true', help='show nuclei predicted')  # show the predicted nuclei in the image
    parser.add_argument('--show_fluo', action='store_true', help='show RFP signal')     # show the RFP signal
    parser.add_argument('--rem_imgs', type=str, help='remove img BF')                   # remove images
    parser.add_argument('--rem_bad_pics', action='store_true', help='automatically remove bad BF imgs') # automatically remove blurry, bad quality images
    parser.add_argument('--num_cell', action='store_true', help='show each cell number')  # show the num of the cells for tracking
    parser.add_argument('--save_in', type=str, help='directory where are saved the results')      # alternative folder than "processing" for saving the results
    parser.add_argument('--one_color', action='store_true', help='only one color')                # only one color for segmentation..
    parser.add_argument('--erode_after_pred', action='store_false', help='make erosion step after prediction')
    parser.add_argument('--dilate_after_pred', action='store_true', help='make dilation step after prediction') # used normally for Fillflood
    parser.add_argument('--method', type=int, help='segmentation method', default=2)         # FillFlood or directly from predictions

    return parser
