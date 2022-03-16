'''
Class for controlling the Coolled pe4000
'''

import serial
import time
try:
    from modules.devices.serial_basics import SERIAL_BASICS as SB
except:
    from serial_basics import SERIAL_BASICS as SB

class COOLLED(SB):
    '''
    Cooled pe4000
    '''
    def __init__(self, port=None):
        '''
        '''
        SB.__init__(self)
        self.name = 'coolled'
        self.init_elements()
        self.timeout = -1
        self.keep = -1
        self.id_channel = 0
        self.channels = ['A','B','C','D']
        cl_name = self.__class__.__name__
        # initialize the serial port communication
        self.port_init(f'{cl_name}'.lower(), port=port)

    def test_response(self):
        '''
        Check the communication
        '''
        self.emit('CSS?')
        answer = self.receive()
        return answer

    def init_elements(self):
        '''
        Initialize the wavelength, the intensity,
         the shutter, and LED loading
        '''
        self.lamb = [0,0,0,0]
        self.intens = [0,0,0,0]
        self.shut = [0,0,0,0]
        self.selected = [0,0,0,0]

    def emit(self, mess):
        '''
        Emit toward Cooled, overwrite the method..
        '''
        self.ser.write((mess + '\n').encode()) # no \r !!!!!!

    def receive(self):
        '''
        Receive from Cooled
        '''
        return self.ser.readline().decode("utf-8")

    def load_val_channel(self,j,ch,line,debug=[]):
        '''
        Insert values of intensity, shut and selected in the object self..
        '''
        if 1 in debug: print(j)
        instruct = line.split(ch)[1][:5]             # instruction for the channel ch
        if 2 in debug:
            print(f'instruction is {instruct}')
            print(f'instruct[-3:] {instruct[-3:]}, instruct[1] {instruct[1]}, instruct[0] {instruct[0]}')
        self.intens[j] = instruct[-3:]
        self.shut[j] = True if instruct[1] == "N" else False
        self.selected[j] = True if instruct[0] == "S" else False

    def ask_channels(self, debug=[]):
        '''
        Check values of each channel
        '''
        self.flush()
        self.emit('CSS?')
        for i in range(1):
            line = self.receive() #.split("\n")
            if 1 in debug: print(f'full line CSS is {line}')
            if 'LAM' in line:
                self.lamb[i] = line.split(':')[2]      # loading wavelength
            elif 'CSS' in line:
                line = line[3:]
                if 2 in debug: print(f'line without CSS is {line}')
                for j,ch in enumerate(self.channels):
                    self.load_val_channel(j,ch,line)
        print('***********')
        print(f'self.intens {self.intens}')
        print(f'self.shut {self.shut}')
        print(f'self.selected {self.selected}')

    def ask_wave_length(self, debug=[]):
        '''
        Ask for the current wavelength
        '''
        self.emit('LAMS')
        answer = self.receive()
        print(f'## ask_wave_length answer is {answer}')

    def load_wave_length(self, lamb, debug=[]):
        '''
        Change the current wavelength to the value lamb
        '''
        self.emit('LOAD:' + str(lamb))
        self.ask_wave_length()

    def select_channel(self,chan,intens, debug=[]):
        '''
        '''
        self.emit(f'CS{chan}{intens.zfill(3)}N')
        answer = self.receive()
        print(f'## select_channel answer is {answer}')

    def unselect_channel(self,chan,intens, debug=[]):
        '''
        '''
        self.emit(f'CX{chan}{intens.zfill(3)}F')
        answer = self.receive()
        print(f'## unselect_channel answer is {answer}')

    def set_intensity(self,chan,intens, debug=[]):
        '''
        Set the intensity for one channel
        '''
        self.emit(f'C{chan}I' + str(intens))
        answer = self.receive()
        print(f'## set_intensity answer is {answer}')

    def select_unselect(self, chan, dic_chan, debug=[]):
        '''
        Select or unselect according the value of dic_chan[chan]['selected']
        '''
        if dic_chan[chan]['selected']:
            self.select_channel(chan)
        else:
            self.unselect_channel(chan)

    def prepare_channels(self, dic_chan, debug=[]):
        '''
        Set lambda, set_intensity
        Set shutter off
        '''
        for chan in self.channels:
            self.load_wave_length(dic_chan[chan]['lamb'])
            self.emit(f"CSS{chan}SF{dic_chan[chan]['intens']}")

    def set_channel(self, chan, dic_chan, debug=[]):
        '''
        Set each channel :
          * load the wavelength
          * set the intensity
          *
        '''
        dic_shut = {'on':'N', 'off':'F'}
        self.load_wave_length(dic_chan[chan]['lamb'])
        shut = dic_shut[dic_chan[chan]['shut']]
        self.emit(f"CSS{chan}S{shut}{dic_chan[chan]['intens']}")

    def set(self, dic_chan, debug=[]):
        '''
        Apply the settings contained in dic_chan
        '''
        self.emit('CSF')                    # all channels shut off
        for chan in self.channels:
            self.set_channel(chan, dic_chan)
