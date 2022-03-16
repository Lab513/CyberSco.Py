'''
Class for controlling the gates for microfluidic experiments
'''

import serial
from time import sleep, time
from colorama import Fore, Back, Style
try:
    from modules.devices.serial_basics import SERIAL_BASICS as SB
except:
    from serial_basics import SERIAL_BASICS as SB

class GATES(SB):
    '''
    port COM7

    code Arduino :

    int start = Serial.parseInt();
    int v1 = Serial.parseInt();
    int v2 = Serial.parseInt();
    int v3 = Serial.parseInt();
    int v4 = Serial.parseInt();
    int v5 = Serial.parseInt();

    simple communication :

    for i in range(6):
        ga.set('1\n')
    '''
    def __init__(self):
        '''

        '''
        cl_name = self.__class__.__name__
        self.port_init(f'{cl_name}'.lower())
        self.name = 'gate'

    def emit(self, mess):
        '''
        Emit on the serial port
        '''
        self.ser.write((mess + '\n').encode())

    def set(self, comm, debug=[]):
        '''
        Send the command comm
        '''
        self.comm = str(comm)
        for bit in self.comm:
            self.emit(bit)
        if 0 in debug:
            print(f'#### set gates at value {self.comm}')

    def set_pos(self, pos, val):
        '''
        Set position pos at value val
        '''
        self.val = val
        ll = list(self.comm)
        ll[pos] = str(val)
        self.comm = ''.join(ll)
        self.set(int(self.comm))

    def set_pos_indices(self, indices, val):
        '''
        Set position pos at value val
        '''
        self.val = val
        ll = list(self.comm)
        for p in indices:
            ll[p] = str(val)
        self.comm = ''.join(ll)
        self.set(int(self.comm))

    def time_elapsed(self, freq=1):
        '''
        freq : frequence in minutes
        '''
        telapsed = int((time() - self.t0)/60)
        if telapsed % freq == 0:
            print(f'time elpased is {telapsed} min')

    def one_on_one_off(self, i, on_value, delay_on, delay_off):
        '''
        Turn on the leds (during delay_on)
        and then turn them off (during delay_off)
        '''
        print(f'{i}th repeat')
        print(Fore.GREEN + "on")
        self.set(on_value)
        sleep(delay_on)
        print(Fore.RED + "off")
        self.set(100000)       # all gates off
        sleep(delay_off)

    def clean_microflu(self, delay_on=1, delay_off=1, repeat=1000):
        '''
        Clean the pipes for microfluidic
        repeat : nb of repetition of "on/off"
        '''
        self.t0 = time()
        for i in range(repeat):
            self.one_on_one_off(i, '111111', delay_on, delay_off)
            self.time_elapsed()
        print(Style.RESET_ALL)

    def clean_microflu_select(self, delay_on=1, delay_off=1, repeat=1000, port=None):
        '''
        Clean the pipes for microfluidic
        repeat : nb of repetition of "on/off"
        port : 100011 will trigger on and off the port 4 and 5
        delay_on : delay on
        delay_off :
        '''
        self.t0 = time()
        print(Fore.RED + "off")
        self.set(100000)       # all gates off
        for i in range(repeat):                                       # selected gates on
            self.one_on_one_off(i, port, delay_on, delay_off)
            self.time_elapsed()
        print(Style.RESET_ALL)

    def test_gates_one_by_one(self, repeat=5):
        '''
        Test one gate after another
        repeat : nb of repetitions for each gate
        '''
        self.set(100000)            # set at 0
        for i in range(1,6):        # gates one to five
            for j in range(repeat):
                self.set_pos(i,1)   # on
                sleep(1)
                self.set_pos(i,0)   # off
                sleep(1)

    def init_gate(self,comm):
        '''
        Used in run.py for setting correctly the gates to the right value
        '''
        self.comm = str(comm)
        for i in range(5):
            sleep(0.1)
            self.set(comm)
