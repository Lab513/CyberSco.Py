#!/usr/bin/env python
# encoding: utf-8
"""
define_all_pages.py
Build the variables used by jinja needed for the views
"""

import glob
import re
import os
import os.path as op
opd, opb, opj = op.dirname, op.basename, op.join


dashboard_subtitle = ""


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
        self.header['presentation_dashboard'] = ""
        # first page image
        self.header['background'] = 'static/imgs/old_new_µscope5_dashboard.jpg'

        # Footer

        self.footer['background'] = op.join('static/img/black.jpg')
        self.footer['copyright'] = "CyberScoPy Dashboard version 0.9"


class define_firstpage(define_page):
    def __init__(self):
        '''
        Welcome page with link for login.
        '''
        define_page.__init__(self)
        self.header['main_title'] = 'Welcome in \n the Dashboard'
        ###
        self.body['main_title'] = ""
        self.body['subtitle'] = ""
        self.body['explanations'] = " "
        self.body['begin'] = u"Begin \u2192"


class define_index_page(define_page):
    def __init__(self, user=None, debug=[]):
        '''

        '''
        define_page.__init__(self)
        if 1 in debug:
            print(f'User is {user}')
        # extract the username from <User username> format..
        username = re.findall('\<User\\s*(\\w+?\\s*\\w*)\\s*\>', str(user))[0]
        self.current_user = username
