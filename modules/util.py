import sys
import os
op = os.path
opj, opd, opb = op.join, op.dirname, op.basename


class Logger(object):
    '''
    Logger for mda experiment
    '''
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(opj('mda_temp', 'log.dat'), "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
