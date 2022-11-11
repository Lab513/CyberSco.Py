#!/usr/bin/env python
# encoding: utf-8

"""
 plot_bokeh.py
 Library for replacing transparently Matplotlib by Bokeh

 *******************************************************************
"""

import os
import numpy as np
import bokeh.plotting as bk
from bokeh.models import Range1d, ColumnDataSource,\
                HoverTool, CustomJS
from bokeh.plotting import output_file
from itertools import cycle


class BOKEH_PLOT(object):
    '''
    Mimicking Matplotlib library with Bokeh
    Usage eg:
        plt = BOKEH_PLOT()
        x = np.arange(120)
        plt.plot(x, x**2, 'r', label='simple square')
        plt.title("first")
        plt.xlabel("x")
        plt.ylabel("y")
        plt.show()
        plt.savefig('first_fig.html')
    '''
    def __init__(self, zoom=None, color='olive', bokeh_range=None,
                 path_file="bk.html", plot_width=500, plot_height=500,
                 bkfig=None, margin_up_down=True, debug=False):
        self.debug = debug
        self.zoom = zoom
        self.color = color
        self.bokeh_range = bokeh_range
        self.plot_width = plot_width
        self.plot_height = plot_height
        self.bkfig = bkfig
        self.xlab = None             # xlabel
        self.ylab = None             # ylabel
        self.tit = None              # Title
        self.path_file = path_file   # Path for storing the html file
        # adding an index when multiple files for same path_file
        self.index_path_file = 1
        self.figure(show=False)
        self.list_plot = []          # list for recording plots informations.
        self.type = 'bokeh'
        self.margin_up_down = margin_up_down
        self.reverse = False

    def plot(self, x, y, kindline_and_color='-',
             label=None, size_val=3, static_label=None, debug=[]):
        '''
        Record plot coordinates and label
        Parameters:
            * x: x axis, list or numpy array
            * y: y axis, list or numpy array
            * kindline_and_color: example : "r--"
            * label: label for the given curve
        '''
        if 0 in debug:
            print("####### In plot  !!!  ")
        if 1 in debug:
            print(f"### x : {x}  ")
            print(f"### y : {y}  ")
        self.static_label = static_label
        size = [size_val]*len(x)
        diccol = {'r': 'red', 'b': 'blue', 'g': 'green',
                  'o': 'orange', 'k': 'black', 'm': 'magenta', 'f': 'grey'}
        first = kindline_and_color[0]
        if first.isalpha():
            col = first
            if kindline_and_color[1:] != '':
                kindline = kindline_and_color[1:]
            else:
                kindline = '-'
        else:
            col = next(self.coliter)  # renewed at each figure call
            kindline = kindline_and_color
        # transform to np.array
        if type(x) == list:
            x = np.array(x)
        if type(y) == list:
            y = np.array(y)
        ##
        dic_kindline = {'-': 'solid', '--': 'dashed', '*': 'dotted'}
        self.list_plot.append({'x': x, 'y': y,
                               'label': label, 'color': diccol[col],
                               'kindline': dic_kindline[kindline],
                               'size': size})  # 'tap': tap,
        self.showed = False
        self.fig = False

    def semilogx(self, x, y, kindline_and_color='-', label=None,
                 size_val=3, static_label=None,
                 reverse=True, debug=[]):
        '''
        At first not using log
        '''
        if 0 in debug:
            print("####### In semilogx  !!!  ")
        self.plot_type = 'logx'
        self.reverse = reverse
        if debug > 0:
            print(f"####### In semilogx  x min is {x.min()}  !!!")
        return self.plot(x, y, label=None, tap=False, size_val=3,
                         static_label=None,
                         kindline_and_color=kindline_and_color)
        # kindline_and_color='-',

    def semilogy(self, x, y, kindline_and_color='-',
                 size_val=3, static_label=None,
                 reverse=False, debug=0):
        '''
        At first not using log
        '''
        if debug > 0:
            print("####### In semilogy  !!!  ")
        self.plot_type = 'logy'
        self.reverse = reverse
        return self.plot(x, y, label=None, tap=False, size_val=3,
                         static_label=None)  # kindline_and_color='-',

    def xlabel(self, xlabel):
        '''
        xlabel for the plot
        '''
        self.xlab = xlabel

    def ylabel(self, ylabel):
        '''
        ylabel for the plot
        '''
        self.ylab = ylabel

    def title(self, title):
        '''
        Title for the plot
        '''
        self.tit = title

    def figure(self, show=True, debug=0):
        '''
        Create a new figure
        Called with show=False at beginning
        '''
        if debug > 0:
            print("###########   in figure  !!! ")
        # Colors for the plots
        self.coliter = cycle(['b', 'g', 'r', 'm', 'o', 'k'])
        if show:
            if debug > 0:
                print("make show")
            self.show()
        self.namefig = self.path_file[:-5] +\
            str(self.index_path_file) + '.html'
        output_file(self.namefig)
        if debug > 0:
            print("making figure : ", self.namefig)
        self.index_path_file += 1
        self.TOOLS = "undo, redo, crosshair, "\
            "pan, wheel_zoom, box_zoom, reset, save"    # Tools for Bokeh
        # box_select

        #### Reinitialize

        self.xr = None
        self.yr = None
        if debug > 1:
            print("in figure, self.xr ", self.xr)
            print("in figure, self.yr ", self.yr)

    def legend(self):
        pass

    def find_range(self, debug=[]):
        '''
        Find Range for calculating self.xr and self.yr
        '''
        if 0 in debug:
            print("####### In find_range  !!!  ")
        if 1 in debug:
            print(f"## self.list_plot {self.list_plot} !!!")
        xmin = self.list_plot[0]['x'][0]                      # x0
        xmax = self.list_plot[0]['x'][-1]                     # last x
        ymin = self.list_plot[0]['y'][0]
        ymax = self.list_plot[0]['y'][-1]
        for l in self.list_plot:
            if l['x'][0] < xmin:
                xmin = l['x'][0]
            if l['x'][-1] > xmax:
                xmax = l['x'][-1]
            if l['y'].min() < ymin:
                ymin = l['y'].min()
            if l['y'].max() > ymax:
                ymax = l['y'].max()
        if self.margin_up_down:
            deltay = ymax-ymin
            ymin, ymax = ymin-deltay*0.1, ymax + deltay*0.1  # margin on y
        if 2 in debug:
            print("l['y'].max()  ", l['y'].max())
            print("xmin, xmax, ymin, ymax ", xmin, xmax, ymin, ymax)
            print("self.bokeh_range ", self.bokeh_range)
            print("self.xr {0}, self.yr {1} ".format(self.xr, self.yr))
        if self.bokeh_range:
            self.xr, self.yr = self.bokeh_range
        else:
            if not self.xr:
                if 3 in debug: print("### range x not yet defined !!! ")
                try:
                    if self.reverse:
                        # x range for Bokeh at reverse
                        self.xr = Range1d(start=xmax, end=xmin)
                except:
                    # x range for Bokeh
                    self.xr = Range1d(start=xmin, end=xmax)
            if not self.yr:
                if 3 in debug:
                    print("### range y not yet defined !!! ")
                # y range for Bokeh
                self.yr = Range1d(start=ymin, end=ymax)
            if 1 in debug:
                print(f"######### in find range "
                      "  ymin is {ymin}, ymax is {ymax}")

    def mouseaxis(self, xname, yname):
        self.xname = xname
        self.yname = yname

    def hovermouse(self):
        '''
        Show mouse coordinates
        '''
        s = ColumnDataSource(data=dict(x=[0], y=[0]))  # points of the line

        callback = CustomJS(args=dict(s=s), code="""
        var geometry = cb_data['geometry'];
        var x_data = geometry.x; // mouse x position in plot coordinates
        var y_data = geometry.y; // mouse y position in plot coordinates
        console.log("(x,y)=" + x_data+","+y_data);
        var x = s.get('data')['x'];
        var y = s.get('data')['y'];
        x[0] = x_data;
        y[0] = y_data;
        s.trigger('change');
        """)

        hover = HoverTool(callback=callback, tooltips="""
                <div id="static-tooltip" style="background-color:#fff7e6 " >
                <span style="font-size: 14px;"> {0}: @x  </span>
                <span style="font-size: 14px;"><br> {1}: @y </span>
                </div>
            """.format(self.xname, self.yname))
        self.bkf.add_tools(hover)                   # Add tool to the figure
        self.bkf.circle(x='x', y='y', source=s)

    def hoverlegend(self, l, genhover, debug=0):
        '''

        Legend compacified with hover tool

        '''
        if debug > 0:
            print("####### In hoverlegend  !!!  ")
        # Make the label only if there is a label registered.
        if l['label']:
            infohover = next(genhover)             # syntax for Python3.

            #deltay = self.ymax
            if debug > 0:
                print(f"########## making hover "
                      "legend, current plot for {l['label']} !!!!!!!!")
            source = ColumnDataSource(
            data=dict(
                x=[infohover['x']],
                y=[infohover['y']],
                desc=[l['label']],
                col=[l['color']],
               )
             )
            hover = HoverTool(
                tooltips="""
                <div >
                    <div>
                        <span style="font-size: 15px; ">@desc</span>
                        <span style="font-size: 15px; color: #696;">    </span>
                    </div>
                </div>
                """, names=[infohover['id']]
              )

            self.bkf.square('x', 'y', size=10, name=infohover['id'],
                            color=l['color'], source=source)
            self.bkf.add_tools(hover)               # Add tool to the figure
            if debug > 0:
                print('added hover !!!')

    def show(self, show_logo=False, save=True, debug=[]):
        '''
        Parameters:
            * show_logo : if True show Bokeh logo
            * save : if True don't show figure and just save.
        '''
        if 0 in debug:
            print("####### In plot_bokeh.show  !!!  ")
        self.find_range()
        if 1 in debug:
            print(f" 'x_range': {self.xr}, 'y_range': { self.yr}")
        dbk = {'tools': self.TOOLS, 'x_range': self.xr, 'y_range': self.yr,
               'title': self.tit, 'x_axis_label': self.xlab,
               'y_axis_label': self.ylab, 'plot_width': self.plot_width,
               'plot_height': self.plot_height}   # Parameters for the plot
        try:
            if self.plot_type == 'logx':
                dic_logx = {'x_axis_type':"log"}
                dbk.update(dic_logx)
        except:
            if 0 in debug:
                print("## self.plot_type 'logx' does not exist")
        try:
            if self.plot_type == 'logy':
                dic_logy = {'y_axis_type':"log"}
                dbk.update(dic_logy)
        except:
            if 0 in debug:
                print("## self.plot_type 'logy' does not exist")
        if self.bkfig:
            # Take the existing figure
            self.bkf = self.bkfig
        else:
            if 0 in debug:
                print("# create new figure")
            # Creates a new figure for original spectrum
            self.bkf = bk.figure(**dbk)
            if 1 in debug :
                print(" dir(self.bkf) ", dir(self.bkf))
        try:
            if self.xname:
                self.hovermouse()
        except:
            if 0 in debug:
                print("no mouse coordinates")
        try:
            try:
                # Generate information for hover legend
                genhover = infos_hover(self.list_plot, self.ymax).gen()
            except:
                # Generate information for hover legend
                genhover = infos_hover(self.list_plot).gen()
        except:
            print('no infos_hover possible.. ')
        for _, l in enumerate(self.list_plot):
            try:
                self.hoverlegend(l, genhover)
            except:
                print('no hoverlegend')
            if 1 in debug:
                print("l['kindline'] ", l['kindline'])
            if l['kindline'] != 'dotted':
                if 0 in debug:
                    print("######### using lines")
                try:
                    if self.static_label:
                        legend = l['label']
                    else:
                        legend = None
                except:
                    legend = None
                try:
                    if (self.plot_type == 'logx') or\
                                (self.plot_type == 'logy'):
                        if debug > 0:
                            print(f'#### Using '
                                  'self.plot_type {self.plot_type}')
                        # Log plot
                        self.bkf.line(l['x'], l['y'], line_width=1,
                                      line_color=l['color'],
                                      legend_label=legend)
                except:
                    # print(f'legend is {legend}')
                    if legend:
                        # Linear plot
                        self.bkf.line(l['x'], l['y'], line_color=l['color'],
                                      legend_label=legend,
                                      line_dash=l['kindline'])
                    else:
                        self.bkf.line(l['x'], l['y'], line_color=l['color'],
                                      line_dash=l['kindline'])   # Linear plot
            else:
                if 0 in debug:
                    print("### Using self.bf.circle ")
                self.bkf.circle(l['x'], l['y'], line_color=l['color'],
                                fill_color=l['color'], legend_label=l['label'],
                                size=l['size'])  # Make points plot
        try:
            # Center the title (by default on the left)
            self.bkf.title.align = 'center'
        except:
            if debug > 0:
                print("no attribute align for title")
        if not show_logo:
            self.bkf.toolbar.logo = None       # Hide the Bokeh logo
        if save:
            bk.save(self.bkf)            # save the plot without showing it.
        else:
            bk.show(self.bkf)           # show the plot in the browser
        self.list_plot = []
        self.showed = True
        if self.debug:
            print("##### showed")
        if self.fig:
            os.rename(self.namefig, self.namehtml)
        self.fig = False
        # Necessary for reinitialize all the parameters xlim, ylim etc...
        # self.figure(show=False)

    def xlim(self, xmin, xmax, debug=0):          # x limits for the plot
        '''
        Limits in x for the plot
        '''
        if debug > 1:
            print(f"defining xmin: {xmin} and xmax:{xmax} ")
        self.xr = Range1d(start=xmin, end=xmax)

    def ylim(self, ymin, ymax, debug=0):          # y limits for the plot
        '''
        Limits in y for the plot
        '''
        if debug > 1:
            print(f"defining ymin: {ymin} and ymax:{ymax} ")
        self.ymax = ymax
        self.yr = Range1d(start=ymin, end=ymax)

    def savefig(self, namehtml, debug=0):
        '''
        Rename figure
        Parameters:
            * namehtml : name of the html bokeh file.
        '''
        if debug > 0:
            print(f"### Bokeh savefig as {namehtml} ")
        if self.showed:
            if debug > 0:
                print("######", self.namefig)
            try:
                os.remove(namehtml)                # remove before saving
            except:
                pass
            os.rename(self.namefig, namehtml)
        else:
            self.fig = True
            self.namehtml = namehtml


class infos_hover():
    '''
    Find corner and increment position down in y direction.
    '''
    def __init__(self, list_plot, ylim_max=None, debug=[]):
        if 1 in debug:
            print(f"l['x'] is {l['x']} ")
            print(f"l['y'] is {l['y']} ")
        self.xmax = 0
        self.ymax = 0
        # Find the maximum in x,y in all the plots for a single figure.
        for l in list_plot:
            llx = list(l['x'])
            lly = list(l['y'])
            if self.xmax < max(llx):
                self.xmax = max(llx)*0.9
            if self.ymax < max(lly):
                self.ymax = max(lly)*0.9
            if ylim_max:
                self.ymax = ylim_max*0.9
        self.index = -1
    # Generator for producing informations for the hover square tool.

    def gen(self):
        while 1:
            self.index += 1
            yield {'x': self.xmax, 'y': self.ymax*(1-0.05*self.index),
                   'id': str(self.index)}


if __name__ == '__main__':

    # instantiate Bokeh in replacement to Matplotlib
    plt = BOKEH_PLOT(debug=False)
    print(dir(plt))
    #####
    print("############## example 1 ###############")
    x = np.arange(120)
    plt.plot(x, x**2, 'r--', label='simple square')
    plt.title("fig 1")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.savefig('fig1.html')
    plt.figure()
    #################
    print("############## example 2 ###############")
    plt.plot(x, -x**3-2*x**2+4, 'g-', label='curve')
    plt.title("fig 2")
    plt.xlabel("xsec")
    plt.ylabel("ysec")
    plt.ylim(-2e6, -5e5)
    plt.savefig('fig2.html')
    plt.figure()
    #################
    print("############## example 3 ###############")
    ll = ["http://www.colors.commutercreative.com/orange/"]*x.size
    path = 'file://' + os.getcwd()
    plt.plot(x, -x**2*2+4, 'k*', label='curve dot')
    plt.title("fig 3")
    plt.plot(x, x**3+4*x, 'r*', label='sec curv dotted')  # , tap=ll
    plt.xlabel("xx")
    plt.ylabel("yy")
    plt.xlim(20, 60)
    plt.ylim(-1e5, 7e5)
    plt.savefig('fig3.html')
    plt.figure()
    #################
    print("############## example 4 ###############")
    plt.plot([0, 20], [0, 20], 'r-')  # , label='curve'
    x = np.arange(120)
    plt.plot(x, x**2, 'g')  # label='simple square'
    plt.title("fig 4")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.savefig('fig4.html')
    plt.figure()
    print("############## example 5 ###############")

    plt.plot(x, -x**3-2*x**2+4, 'g-')  # , label='blabla'
    plt.title("fig 5")
    plt.xlabel("xsec")
    plt.ylabel("ysec")
    plt.ylim(-2e6, -5e5)
    plt.mouseaxis('T2', 'ampl')
    plt.show()

    plt.savefig('fig5.html')
