import time
from time import sleep
from colorama import Fore, Style              # Color in the Terminal

class ZPOS():
    '''
    Zpos for Olympus IX81
    '''
    def __init__(self):
        '''
        position expressed in hundredth of µm
        '''
        self.nbbytes = 11                    # number of bytes for the receive
        self.lim_nbtry = 20

    def retrieve_pos(self, debug=[]):
        '''
        '''
        if 1 in debug: print('in retrieve position')
        self.flush()
        self.emit('2POS?')
        sleep(0.1)
        answer = self.receive(self.nbbytes)
        if 1 in debug: print(f'answer for posz is {answer}')
        try:
            val = answer.split()[1].strip()
            kind = answer.split()[0].strip()
        except:
            return False, 0
        if 1 in debug: print(f'val in ask_zpos is {val}')
        if kind == '2POS' and len(val) == 6 :
            zpos = int(val)
            return True, zpos
        else:
            return False, 0

    def try_retrieve_posz(self, debug=[]):
        '''
        While not POS in the string and not 6 bytes, ask again for position
        '''
        cnd, zpos = self.retrieve_pos()
        nbtry = 0
        while not cnd and nbtry < self.lim_nbtry:
            cnd, zpos = self.retrieve_pos()
            if 1 in debug: print(f'cnd, zpos are {cnd, zpos} ')
            nbtry += 1
        return zpos

    def ask_zpos(self, debug=[]):
        '''
        As for z position of the objective
        '''
        if 1 in debug: print('asking for pos')
        self.flush()
        for i in range(2):
            zpos = self.try_retrieve_posz()
            if 1 in debug:
                print(f'########## after ask_pos, pos found is  {zpos} !!!!')
        if 2 in debug:
            print(f'########## zpos found is  {zpos} !!!!')
        return zpos

    def try_set_zpos(self, val, move_type='d'):
        '''
        Try to set a new position at value val
         and return the resulting position reached
        '''
        self.emit('2LOG IN')
        self.emit('2MOV '+ move_type + ',' + str(int(val)))
        self.emit('2LOG OUT')
        result = self.ask_zpos()
        return result

    def while_cnd_try(self, val, cnd, move_type):
        '''
        '''
        nbtry=0
        # try until absolute position is found
        while cnd and nbtry < self.lim_nbtry :
            res = self.try_set_zpos(val, move_type=move_type)
            nbtry += 1

    def set_zpos(self, val, move_type='d', debug=[]):
        '''
        Set the position of the objective in absolute or relatively
        val : pos z in hundredth of µm
        move_type :
            d : absolute
            N : relative toward the slide
            F : relative far from the slide
        '''
        if 0 in debug:
            print(Fore.YELLOW +  f'in set_zpos, val is {val}')
            print(Style.RESET_ALL)
        z_init = self.ask_zpos()
        res = self.try_set_zpos(val, move_type=move_type)

        if move_type == 'd' :
            cnd = res != val
            # try until absolute position is found
            self.while_cnd_try(val, cnd, move_type)
        elif move_type == 'F':
            cnd = res != int(z_init - val)
            # try until relative far position is found
            self.while_cnd_try(val, cnd, move_type)
        elif move_type == 'N':
            cnd = res != int(z_init + val)
            self.while_cnd_try(val, cnd, move_type)
        # try until relative near position is found
        if 1 in debug:
            print(f'final zpos for set_pos, val is {res}')

    def go_zpos(self, val, move_type='d', ask=False, debug=[0]):
        '''
        Fast positionning
        val : pos z in hundredth of µm
        '''
        if 0 in debug: print(f'In go_zpos, val = {val} ')
        self.emit('2LOG IN')
        self.emit(f'2MOV {move_type}, {int(val)}, 1, 100000, 49' )
        if ask: self.ask_zpos()
        self.emit('2LOG OUT')
