'''
Class for controlling the Xcite device for fluorescence
#
https://neurophysics.ucsd.edu/Manuals/X-Cite/XciteExacteUsers%20Guide.pdf, p32
'''

import serial
import time
from time import sleep
try:
    from modules.devices.serial_basics import SERIAL_BASICS as SB
except:
    from devices.serial_basics import SERIAL_BASICS as SB

class XCITE(SB):
    '''
    '''
    def __init__(self, port=None):
        '''
        '''
        SB.__init__(self)
        self.name = 'xcite'
        cl_name = self.__class__.__name__
        self.port_init(f'{cl_name}'.lower(), port=port)

    def emit(self, mess):
        '''
        Emit toward XCite
        '''
        self.ser.write((mess + '\r').encode())     # Becareful,  no \n !!!!!

    def connect_to_unit(self, debug=[]):
        '''
        Connexion to unit for serial communication
        '''
        self.emit('tt')
        if 0 in debug:
            print('connect to unit')

    def disconnect_from_unit(self, debug=[]):
        '''
        Connexion to unit for serial communication
        '''
        self.emit('xx')
        if 0 in debug:
            print(f'disconnect from unit')

    def enable_extended_cmd(self, debug=[]):
        '''
        Enable extended commands (all commands on page 36)
        '''
        self.emit('jj')
        answer = self.receive(1)
        if 0 in debug:
            print(f'enable_extended_cmd, answer {answer}')

    def enable_shut(self, debug=[]):
        '''
        Enable shutter control via serial port
        '''
        self.emit('cc')
        if 0 in debug:
            print(f'enable the shutter ')

    def disable_shut(self, debug=[]):
        '''
        Enable shutter control via serial port
        '''
        self.emit('yy')
        if 0 in debug:
            print('disable the shutter')

    def CLF_on(self, debug=[]):
        '''
        Closed-Loop Feedback on (page 24)
        '''
        self.emit('kk')
        if 0 in debug:
            print(f'Closed-Loop Feedback on')

    def CLF_off(self, debug=[]):
        '''
        Closed-Loop Feedback off
        '''
        self.emit('gg')
        if 0 in debug:
            print(f'Closed-Loop Feedback off')

    def set_intens_level(self, percent, debug=[]):
        '''
        Set light intensity in percent
        “dxxx\r” where xxx is the desired intensity
        '''
        self.emit(f'd{str(percent).zfill(3)}')
        answer = self.receive(1)
        if 0 in debug:
            print(f'set_intens_level, answer {answer}')

    def get_intens_level(self, debug=[]):
        '''
        Get light intensity
        '''
        self.emit('dd')
        sleep(1)
        answer = self.receive(3)
        if 0 in debug:
            print(f'current intensity level is {answer}')

    def get_unit_status(self, percent, debug=[]):
        '''
        Get unit status
        '''
        self.emit('uu')
        sleep(1)
        answer = self.receive(3)
        if 0 in debug:
            print(f'unit status is {answer}')

    def shut_on(self, debug=[]):
        '''
        Shutter on
        '''
        self.emit('mm')
        if 0 in debug:
            print(f'shutter on')

    def shut_off(self, debug=[]):
        '''
        Shutter off
        '''
        self.emit('zz')
        if 0 in debug:
            print('shutter off')

    def light_on(self, debug=[]):
        '''
        Light on
        '''
        self.emit('bb')
        if 0 in debug:
            print(f'light on')

    def light_off(self, debug=[]):
        '''
        Light off
        '''
        self.emit('ss')
        if 0 in debug:
            print(f'light off')

    def init_XCite(self):
        '''
        Initialize Xcite device
        Enable functions
        '''
        self.connect_to_unit()
        sleep(0.5)
        self.enable_extended_cmd()
        sleep(0.5)
        self.enable_shut()
        sleep(0.5)
        #self.CLF_off()
        #self.set_intens_level(10)
