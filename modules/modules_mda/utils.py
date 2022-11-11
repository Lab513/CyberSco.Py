
from datetime import datetime
import sys
from modules.util import Logger


class UTILS():
    '''
    '''

    @property
    def date(self):
        '''
        Return a string with day, month, year, Hour and Minute..
        '''
        now = datetime.now()
        dt_string = now.strftime("%d-%m-%Y-%H-%M")
        return dt_string

    def logfile(self):
        '''
        Log file with standard err and output
        '''
        sys.stdout = Logger()
