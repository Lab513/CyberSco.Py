import time

class LAMP():
    '''
    Lamp of Olympus IX81
    '''
    def __init__(self):
        '''
        '''

    def ask_lamp(self):
        '''
        Ask if lamp on or off
        '''
        self.flush()
        self.emit('1LMPSW?')
        answer = self.receive(11)
        print(f'answer is {answer}')
        self.lamp = False if 'OF' in answer else True

    def set_lamp(self, val=None):
        '''
        Lamp on/off
        '''
        self.emit('1LOG IN')
        if val == 'on':
            self.emit("1LMPSW ON")
        elif val == 'off':
            self.emit("1LMPSW OFF")
        self.emit('1LOG OUT')

    def ask_intensity(self):
        '''
        Ask for the current intensity used for BF
        '''
        self.flush()
        self.emit('1LMP?')
        answer = self.receive(8)
        print(f'answer is {answer}')
        self.intens = float(answer.split()[1])/10

    def set_intens(self, intens):
        '''
        Set lamp intensity
        '''
        try:
            self.emit('1LOG IN')
            self.emit('1LMP ' + str(int(float(intens*10))))
            self.emit('1LOG OUT')
        except:
            print(f'Cannot set the Olympus light intensity !!!!')
