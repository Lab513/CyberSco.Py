import time

class WHEEL():
    '''
    Wheel filter of Olympus IX81
    '''
    def __init__(self):
        '''
        '''

    def ask_wheel_filter(self):
        '''
        Ask which filter is used
        '''
        self.flush()
        self.emit('1MU?')
        wheel_filter = self.receive(7)
        print(f'wheel_filter is {wheel_filter}')

    def set_wheel_filter(self, wheel_num):
        '''
        Set which filter is used
        '''
        self.emit('1LOG IN')
        self.emit('1MU ' + str(wheel_num))
        self.emit('1MU?')
        self.emit('1LOG OUT')
        self.curr_wheel = wheel_num
