
from pathlib import Path
from time import sleep, time
from colorama import Fore, Style         # Color in the Terminal
from datetime import datetime as dt
import json
import glob
import shutil as sh
import oyaml as yaml
import os
op = os.path
opd, opb, opj, ope = op.dirname, op.basename, op.join, op.exists


def date():
    '''
    Return a string with day, month, year, hour, minute and seconds
    '''
    now = dt.now()
    dt_string = now.strftime("%d-%m-%Y-%H-%M-%S")  # -%H-%M
    return dt_string
