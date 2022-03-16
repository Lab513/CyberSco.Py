import cv2
import numpy as np
from scipy.linalg import norm
from scipy.interpolate import interp2d
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from matplotlib import pyplot as plt

class FIT_GROWTH():
    '''
    Find the exponential zones and fit an exponential curve.
    '''

    @property
    def dbl_filter_with_SG(self, SG_length=21):
        '''
        Make a double SG filtering
        '''
        nbcells_filtered = savgol_filter(self.arr_nb_cells, SG_length, 2)        # Savisky Golay filter
        dbl_nbcells_filtered = savgol_filter(nbcells_filtered, SG_length, 2)     # iteration of the Savisky Golay filter..
        return dbl_nbcells_filtered

    def debug_intervals_using_diff(self):
        '''
        '''
        plt.figure()
        plt.plot(self.diff_cells)
        plt.figure()
        plt.plot(self.dbl_filter_with_SG)
        plt.show()

    def intervals_using_diff(self, debug=0):
        '''
        Find the intervals using derivative and slope
        '''
        dc = np.diff(self.dbl_filter_with_SG)     # double filtering with Savisky Golay
        dc[dc < self.slope] = 0
        dc[dc > self.slope] = 1
        self.diff_cells = dc
        if debug > 0:
            self.debug_intervals_using_diff()

    def make_list_slices(self,flat_limits):
        '''
        List of slice for fitting
        '''
        delta, limsup, interv  = [], [], []
        for i in range(self.nb_fits):
            if i == 0:
                delta.append(flat_limits[0])
                limsup.append(int(delta[i]*self.ratio_fit))
                interv.append(slice(0,limsup[i]))
            else:
                delta.append(flat_limits[i+1]-flat_limits[i])
                limsup.append(flat_limits[i] + int(delta[i]*self.ratio_fit))
                interv.append(slice(flat_limits[i],limsup[i]))
        return interv

    def find_interv(self, debug=1):
        '''
        Find the intervals for performing the exponential fits.
        '''

        self.intervals_using_diff()
        seg_pos = np.diff(self.diff_cells)            # position of the intervals..
        flat_limits = np.where(seg_pos != 0)[0]       # point diff 0
        flat_limits = flat_limits[ flat_limits > 20 ]   # remove points inferior to limit..
        if debug > 0: print("flat_limits ", flat_limits)
        interv = self.make_list_slices(flat_limits)

        return interv

    def insert_growth_rate(self, i, growth_rate):
        '''
        insert growth rate in video
        '''
        font = cv2.FONT_HERSHEY_SIMPLEX
        posy = 30 + 30*(i+1)
        cv2.putText(self.img, growth_rate, (300, posy), font, 0.5, (255, 255, 255), 2, cv2.LINE_AA)

    def func_exp(self, x, a, b, c):
        '''
        Function for fitting an exponential on growth curves
        '''
        return a * np.exp(b * x) + c

    def fit_growth_curve(self,ax,i,s,debug=0):
        '''
        Fit and plot the exponential growth curve
        '''
        yarray = self.arr_nb_cells[s]
        xarray = np.arange(s.start, s.stop)
        params = curve_fit(self.func_exp, xarray, yarray, bounds=(0, [ 1e2, 1e0, 1e2 ]))     # Perform the exponential fit
        growth_rate = str(round(params[0][1]*self.factor_growth,2))
        yfitted = self.func_exp(xarray,*params[0])
        #ax.plot(xarray, yfitted)                            #  plot the growth curve
        self.list_fits.append([xarray, yfitted])
        self.list_growth_rates.append(growth_rate)
        if debug > 0: print('in enumerate intervals.. ', i)
        try:
            self.insert_growth_rate(i, growth_rate)         # insert growth rate in video..
        except:
            print('cannot insert growth rate in the video')

    def growth_curves(self, ax):
        '''
        Fit the exponentials, calculate and show the growth rate..
        '''
        interv = self.find_interv()         # search the intervals for the fits..
        self.list_fits = []
        self.list_growth_rates = []
        for i,s in enumerate(interv):       # intervals on which are made the fits for the growth rate
            self.fit_growth_curve(ax,i,s)   # fit and plot growth curve..
        ax.legend()

    def make_growth_curves(self, mpl, ax):
        '''
        Build the growth curve
        '''
        if not mpl :                       #
            try:
                self.growth_curves(ax)
            except:
                pass
        else:
            if self.nb_fits > 0:
                self.growth_curves(ax)
                print('#### Fitting curves !!!')
                print("len(self.list_fits) ", len(self.list_fits))
                ax.title('number cells evolution')
                for i,ll in enumerate(self.list_fits):
                    labelgrowth = 'growth rate = ' + self.list_growth_rates[i]
                    ax.plot( ll[0], ll[1], linestyle='--', label = labelgrowth )    # plot the fitting curves

    def add_growth_curve(self, mpl, ax):
        '''
        '''
        arr_cells = np.array(self.arr_nb_cells)
        if self.nb_fits > 0:
            if len(arr_cells[arr_cells > 0]) > 20:        # fitting few points after the beginning
                try:
                    self.make_growth_curves(mpl, ax)          # Fitting exponential curve on BF number of cells extracted..
                except:
                    print('cannot fit on this picture')

    def debug_SG(self):
        '''
        debug Savisky Golay for checking smoothness etc..
        '''
        plt.plot(self.dbl_filter_with_SG)    # check the SG filtering
        plt.figure()
        plt.plot(self.diff_cells)            # check the derivative for finding the intervalls
        plt.show()
