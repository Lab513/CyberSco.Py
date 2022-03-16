import time

class SHUT():
    '''
    Shutter of Olympus IX81
    '''
    def __init__(self):
        '''
        '''

    def ask_shutter(self):
        '''
        ask if the shutter is in or out
        '''
        self.emit('1SHUT1?')
        answer = self.receive(11)
        self.shut = False if 'IN' in answer else True
        if self.shut_ctrl !=-1:
            self.case_shut_cntrl()

    def set_shutter(self, shut=None, debug=[]):
        '''
        Set the shutter to in or out
        '''
        self.flush()
        self.emit('1LOG IN')
        if shut == 'on':
            self.emit('1SHUT1 OUT')
        elif shut == 'off':
             self.emit('1SHUT1 IN')
        self.shut = False if shut == 'off' else True
        self.emit('1SHUT1?')
        answer = self.receive(11)
        if 0 in debug:
            print(f'## set_shutter answer is {answer}')
        self.emit('1LOG OUT')
