import serial
import time
from time import sleep

try:
    from modules.devices.serial_basics import SERIAL_BASICS as SB
except:
    from devices.serial_basics import SERIAL_BASICS as SB

class PRIOR(SB):
    '''
    '''
    def __init__(self, port=None):
        '''
        '''
        SB.__init__(self)             # basics functions for serial connexion
        self.name = 'prior'
        self.steps_per_um = 50         # number of steps in one micrometer
        cl_name = self.__class__.__name__
        # initialize the serial port communication
        self.port_init(f'{cl_name}'.lower(), port=port)

    def test_response(self):
        '''
        Check the communication
        '''
        self.emit('PX')
        answer = self.receive(9)
        return answer

    def receive(self, length):
        '''
        Receive on the serial port
        '''
        return self.ser.read_until(b'\r').decode("utf-8")

    def ask_pos(self, pos, debug=[]):
        '''
        Ask Prior for the position
        pos : 'x' or 'y'
        '''
        dic_pos= {'x': 9, 'y': 8}                  # dic for serial length
        pos_ok = False
        while not pos_ok:
            try:
                self.flush()
                if 2 in debug: print(f'P{pos.upper()}')
                self.emit(f'P{pos.upper()}')              # ask for position
                sleep(0.1)
                answer = self.receive(dic_pos[pos])
                if 2 in debug: print(f'answer is {answer}')
                # current position in µm
                curr_pos = -int(answer[1:])/self.steps_per_um
                pos_ok = True
            except:
                pass
        if 1 in debug: print(f'pos = {curr_pos} µm')
        return curr_pos                       # in µm

    def from_micron_to_step(self, px, py):
        '''
        converting from um to steps
        '''
        # steps in x and y
        return int(px*self.steps_per_um), int(py*self.steps_per_um)

    def absolute_move_to(self, px, py):
        '''
        Absolute displacement in microns
        '''
        px, py = self.from_micron_to_step(px, py)          # px, py in steps
        cmd_pos = f'G,{px},{py}'                        # absolute move
        self.emit(cmd_pos)                          # absolute displacement

    def relative_move_to(self, px, py):
        '''
        Relative displacement in microns
        '''
        px, py = self.from_micron_to_step(px, py)   # px, py in steps
        cmd_pos = f'GR,{px},{py}'                  # relative move
        self.emit(cmd_pos)                      # relative displacement
