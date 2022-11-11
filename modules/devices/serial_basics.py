import serial
import yaml
import time

class SERIAL_BASICS():
    '''

    '''
    def __init__(self):
        '''
        '''
        pass

    def port_init(self, cl_name_low, port=None, debug=[]):
        '''
        Initialisation of the serial port
        '''

        try:
            addr_yaml = f'settings/ports/{cl_name_low}.yaml'
            con = self.load_yaml(addr_yaml)                          # read yaml port file
            if 0 in debug:
                print('loaded the yaml file'
                      f' for the serial connection of {cl_name_low} ')
                print(f"con['port'] is {con['port']}")
        except:
            addr_yaml = f'modules/settings/ports/{cl_name_low}.yaml'
            con = self.load_yaml(addr_yaml)
            if 0 in debug:
                print('loaded the yaml file'
                      f' for the serial connection of {cl_name_low} ')
                print(f"con['port'] is {con['port']}")

        try:
            if port:
                con['port'] = port
            self.ser = serial.Serial(
                port = con['port'],
                baudrate = con['baudrate'],
                bytesize = getattr(serial, con['bytesize']),
                parity = getattr(serial, con['parity']),
                stopbits =  getattr(serial, con['stopbits']),
                xonxoff =  con['xonxoff'],
                timeout = 3
           )
            self.state = 'connected'  # connexion state
            if 1 in debug:
                print(f'Succeeded serial connection for {cl_name_low} ')
        except:
            if 1 in debug:
                print(f'cannot find the port for {cl_name_low} ')
                print('The port is probably yet in used !!!')
            self.ser = 'fake_serial'
            self.state = 'not connected' # connexion state

    def load_yaml(self, addr_yaml):
        '''
        Load the yaml file for the device
        '''
        with open(addr_yaml) as file:
            con = yaml.load(file, Loader=yaml.FullLoader)    # read yaml port file
        return con

    def emit(self, mess):
        '''
        Emit on the serial port
        '''
        self.ser.write((mess + '\r\n').encode())

    def receive(self, length):
        '''
        Receive on the serial port
        '''
        return self.ser.read(length).decode("utf-8")

    def emit_recv(self, mess, length=11):
        '''
        Make both emit and receive
        '''
        self.emit(mess)
        answer = self.receive(length)
        print(answer)

    def flush(self):
        '''
        Clean input and output
        '''
        self.ser.flushInput()
        self.ser.flushOutput()

    def close(self):
        '''
        '''
        print('closing the connexion')
        self.ser.close()
