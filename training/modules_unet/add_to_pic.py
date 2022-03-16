import os
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import cv2

class ADD_TO_PIC():
    '''
    Add objects to pictures
    '''

    def insert_curve_cell_nb(self):
        '''
        Curve showing the evolution of the cells number..
        '''
        size_sub = 250
        fig = Figure(figsize=(5, 4), dpi=100)
        canvas = FigureCanvasAgg(fig)
        ax = fig.add_subplot(111)
        self.draw_curves(ax)                 # Draw the data and the fitting curves.
        canvas.draw()
        buf = canvas.buffer_rgba()
        graph_img = np.asarray(buf)
        res = cv2.resize(graph_img, dsize=(size_sub, size_sub), interpolation=cv2.INTER_CUBIC)
        self.img[:size_sub, :size_sub] = 150     # white background for curve
        self.img_mask[:size_sub, :size_sub] = res[:,:,:3]

    def insert_cell_nb(self, num):
        '''
        Insert the nb of cells in the video..
        '''
        font = cv2.FONT_HERSHEY_SIMPLEX
        txt_nb_cells = 'nb cells = ' + str(self.arr_nb_cells[num])
        txt_col = (255, 255, 255)
        cv2.putText(self.img, txt_nb_cells, (300,30), font, 0.5, txt_col, 2, cv2.LINE_AA)

    def make_ellipses(self, contours):
        '''
        Ellipses around the cells..
        '''
        elsz_max = 20
        for i,cnt in enumerate(contours):
            try:
                ell = cv2.fitEllipse(cnt)
                if ell[1][0] < elsz_max and ell[1][1] < elsz_max:
                    #cv2.ellipse(self.img_mask, ell, (0, 0, 255), 2)
                    cv2.ellipse(self.img, ell, (0, 0, 255), 1)
                else:
                    print("axis to large !!! ")
            except:
                print('no ellipse for contour n° {0} '.format(i))
