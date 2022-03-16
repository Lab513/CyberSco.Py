#!/usr/bin/env python
# encoding: utf-8
"""
define_all_pages.py
Build the variables used by jinja needed for the views
"""

import glob
import os.path as op
opd, opb, opj = op.dirname, op.basename, op.join

Interface_subtitle = ""


class define_page(object):
    '''
    General template
    '''
    def __init__(self):
        self.body = {}
        self.header = {}
        self.footer = {}

        # Body

        self.body['main_title'] = ""
        self.body['subtitle'] = ""
        self.body['explanations'] = ""

        # Header

        self.header['main_title'] = ""
        self.header['presentation_interface'] = ""
        # first page image
        self.header['background'] = 'static/imgs/old_new_µscope5.jpg'

        # Footer

        self.footer['background'] = op.join('static/img/black.jpg')
        self.footer['copyright'] = "CyberScoPy version 0.9"


class define_firstpage(define_page):
    def __init__(self):
        '''
        Welcome page with link for login.
        '''
        define_page.__init__(self)
        self.header['main_title'] = 'CyberSco.py'
        self.header['mess'] = 'Conditional Microscopy'
        self.header['presentation_interface'] = 'A more flexible Microscopy'
        ###
        self.body['main_title'] = ""
        self.body['subtitle'] = ""
        self.body['explanations'] = " "
        self.body['begin'] = u"Begin \u2192"


class define_index_page(define_page):
    def __init__(self):
        '''
        Page (index_folder.html) for entering
         the parameters and launching the processings.
        '''
        define_page.__init__(self)
        # list of the protocols
        self.prot = [opb(f).split('.yaml')[0] for f
                     in glob.glob('interface/static/mda_protocols/*.yaml')]
        self.prot.remove('temp0')
