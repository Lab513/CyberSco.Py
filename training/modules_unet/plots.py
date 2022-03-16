from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt

class PLOTS():
    '''
    Plots
    '''

    def set_plot_params(self):
        '''
        Set plot parameters for comparison between OTSU and u-net
        '''
        text_size = 12
        self.fig.text(0.5, 0.03, 'frames', ha='center', va='center', size = text_size)     # xlabel : frames
        self.fig.text(0.04, 0.5, 'nb cells', ha='center', va='center', rotation='vertical', size = text_size)   # ylabel : nb cells
        plt.subplots_adjust(hspace=0.3, wspace=0.3)
        plt.tick_params(labelcolor='none', top=False, bottom=False, left=False, right=False)

    def prepare_plots(self, nbcols = 2):
        '''
        Prepare plots for comparison between OTSU and u-net with different thresholds
        '''
        lcnc = len(self.list_curv_nb_cells)  # length of the list of the graphs of the evolution of the number of cells
        print("lcnc ", lcnc)
        nblines = lcnc//nbcols #+ 1
        print("nbcols {0}, nblines {1} ".format(nbcols, nblines))
        self.fig, self.axs = plt.subplots(nblines, nbcols, figsize=[10,7])
        self.set_plot_params()
        self.nbcols, self.nblines = nbcols, nblines

    def thresh_subplot(self,i,cnc,lth):
        '''
        Subplot for optim threshold
        '''
        s = i//self.nbcols, i%self.nbcols
        print('s is ',s)
        if self.args.rfp:       # plot RFP
            self.axs[s].plot(self.cf.list_nb_cells[:self.length], linewidth=1, label='OTSU')
        self.axs[s].plot(cnc, linewidth=1, label='u-net')     # plot BF
        self.axs[s].set_title( 'thresh = ' + str( lth[i] ) )  # current threshold

    def separated_plots_for_test_thresh(self,lth):
        '''
        Set of plots for the threshold comparison
        '''
        self.prepare_plots()
        for i,cnc in enumerate(self.list_curv_nb_cells):
            self.thresh_subplot(i,cnc,lth)
        plt.legend()
        self.fig.suptitle('Cells counting, optimal threshold',size=15)
        dic_cells_curve = { 'film': self.name_film, 'model': self.model, 'date': self.date}
        plt.savefig( 'thresh_effect_{film}_{model}_{date}.png'.format( **dic_cells_curve ) )

    def set_axes(self,ax):
        '''
        Axes for plot of number of cells
        '''
        try:
            ax.xlabel('frames')
            ax.ylabel('number of cells')
        except:
            ax.set_xlabel('frames')           # subplot case
            ax.set_ylabel('number of cells')
        try:
            ax.set_ylim([ 0, self.max_nb_cells ])
        except:
            ax.ylim([ 0, self.max_nb_cells ])

    def draw_curves(self, ax, mpl=False):
        '''
        Data and fitting curves
        '''
        self.set_axes(ax)
        ax.plot(self.arr_nb_cells, label='u-net')            # curve of the number of cells from BF images
        if self.args.rfp:
            ax.plot(self.cf.list_nb_cells, label='OTSU RFP')  # curve of the number of cells from RFP images
        self.add_growth_curve(mpl, ax)                        # fitting exponential curves

    def save_graph_nb_cells(self):
        '''
        Save the figure of the nb of cells in function of the frames..
        '''
        dic_cells_curve = { 'film': self.name_film, 'model': self.model,
                            'thresh': self.thresh_after_pred, 'date': self.date }
        addr_file_nb_cells = self.dir_result / 'nb_cells_curve_{film}_{model}_th{thresh}_{date}.png'.format( **dic_cells_curve )
        print("#### addr_file_nb_cells {0} ".format(addr_file_nb_cells))
        plt.savefig( addr_file_nb_cells )

    def find_max_nb_cells(self, im):
        '''
        Find an approximation of max number of cells with last image
        '''
        self.load_image_and_mask(im)
        ##
        if self.thresh_after_pred:
            self.img_mask[ self.img_mask > self.thresh_after_pred ] = 255        # enhance the prediction mask
        contours = self.find_contours(self.img_mask, save_cntrs=False)
        self.max_nb_cells = int( len(contours) * 1.3 )
        print("###self.max_nb_cells is ", self.max_nb_cells)
