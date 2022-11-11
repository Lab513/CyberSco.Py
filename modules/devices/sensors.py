'''
Class for sensors (temperature, luminosity etc..)
'''

import serial
from time import sleep, time
from colorama import Fore, Back, Style
try:
    from modules.devices.serial_basics import SERIAL_BASICS as SB
except:
    from serial_basics import SERIAL_BASICS as SB

class SENSORS(SB):
    '''
    port COM7

    '''
    def __init__(self):
        '''
        Init sensor class
        '''
        cl_name = self.__class__.__name__
        self.port_init(f'{cl_name}'.lower())
        self.name = 'sensors'

    def read(self):
        '''
        Read from sensors..
        '''
        mess = self.ser.readline()

        return mess.decode('utf-8')
