'''
MDA params
'''

from interface.flask_app import *
from interface.modules.misc_import import *
from interface.modules.AF import *
from interface.modules.init.init_params import *

def mda_params(mda):
    '''
    Retrieve parameters for the mda
    kind_focus : AF_ML, ZDC etc..
    afml_optim  : max, max_righ, max_left
    '''
    mda.kind_focus = kind_focus
    mda.afml_optim = afml_optim
    mda.monitor_params = monitor_params

    return mda
